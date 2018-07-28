# MIT License
#
# Copyright (c) 2017-18 Felix Simkovic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'Felix Simkovic'
__version__ = '1.0'

from tempfile import NamedTemporaryFile

import abc
import logging
import os

from pyjob.exception import PyJobError 
from pyjob.misc import EXE_EXT, SCRIPT_HEADER, SCRIPT_EXT, is_script

logger = logging.getLogger(__name__)

ABC = abc.ABCMeta('ABC', (object, ), {})



class Queue(ABC):

    def __init__(self):
        self.pid = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.wait()
        self.kill()

    def close(self):
        self.wait()
        self.kill()

    @abc.abstractmethod
    def kill(self):
        pass

    @abc.abstractmethod
    def submit(self):
        pass
    
    @abc.abstractmethod
    def wait(self):
        pass

    @staticmethod                                                                                                       
    def check_script(script):                                                                                           
        """Check if all scripts are sound"""                                                                            
        if isinstance(script, str) and is_script(script):                                                               
            logs = [script.rsplit('.', 1)[0] + '.log']                                                                  
            scripts = [script]                                                                                          
        elif (isinstance(script, list) or isinstance(script, tuple)) and all(is_script(fpath) for fpath in script):        
            logs = [s.rsplit('.', 1)[0] + '.log' for s in script]                                                       
            scripts = list(script)                                                                                      
        else:                                                                                                           
            raise PyJobError("One or more scripts cannot be found or are not executable")                               
        return scripts, logs        


class ClusterQueue(Queue):

    def __init__(self):
        self.queue = []

    def prep_array_script(self, scripts, directory):
        array_jobs = NamedTemporaryFile(delete=False, dir=directory, prefix='array_', suffix='.jobs').name
        logger.debug('Writing array jobs script to %s', array_jobs)
        with open(array_jobs, 'w') as f_out:
            f_out.write(os.linesep.join(scripts) + os.linesep)
        array_script = array_jobs.replace('.jobs', '.script')
        logger.debug('Writing array master script to %s', array_script)
        content = [
            SCRIPT_HEADER,
            'script=$(awk "NR==$' + self.__class__.TASK_ENV + '" ' + array_jobs + ')',
            "log=$(echo $script | sed 's/\.sh/\.log/')",
            '$script > $log 2>&1' + os.linesep
        ]
        with open(array_script, 'w') as f_out:
           f_out.write(os.linesep.join(content))
        return array_script, array_jobs
