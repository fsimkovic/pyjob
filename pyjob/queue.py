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

from importlib import import_module
from tempfile import NamedTemporaryFile

import abc
import logging
import os

from pyjob.exception import PyJobError, PyJobUnknownQueue
from pyjob.misc import EXE_EXT, SCRIPT_HEADER, SCRIPT_EXT, is_script

ABC = abc.ABCMeta('ABC', (object, ), {})

# TODO: make this dynamic
QUEUES = {
    'local': ('pyjob.local', 'LocalJobServer'),
    'lsf': ('pyjob.lsf', 'LoadSharingFacility'),
    'pbs': ('pyjob.pbs', 'PortableBatchSystem'),
    'sge': ('pyjob.sge', 'SunGridEngine'),
    'torque': ('pyjob.pbs', 'PortableBatchSystem'),
}

logger = logging.getLogger(__name__)


def QueueFactory(platform, *args, **kwargs):
    """Accessibility function for any :obj:`~pyjob.queue.Queue`
    
    Parameters
    ----------
    platform : str
       The platform to create the queue on
    *args : tuple
       Any positional arguments relevant to the :obj:`~pyjob.queue.Queue`
    **kwargs : dict
       Any keyword arguments relevant to the :obj:`~pyjob.queue.Queue`

    Raises
    ------
    :exc:`~pyjob.exception.PyJobUnknownQueue`
       Unknown queue

    """
    platform = platform.lower()
    if platform in QUEUES:
        logger.debug('Found requested platform in available queues')
        module, class_ = QUEUES[platform]
        return getattr(import_module(module), class_)(*args, **kwargs)
    else:
        raise PyJobUnknownQueue('Unknown queue: %s' % platform)


class Queue(ABC):
    """Abstract Base Class to create new :obj:`~pyjob.queue.Queue` objects with
    """

    TASK_ENV = None
    ARRAY_TASK_ID = TASK_ENV

    def __init__(self, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.queue.Queue`"""
        for i, arg in enumerate(args):
            logger.debug('Ignoring positional argument [%d]: %d', i, str(arg))
        for k, v in kwargs.items():
            logger.debug('Ignoring keyword argument [%s]: %s', str(k), str(v))

    def __enter__(self):
        """Contextmanager entry function
        
        Note
        ----
        For further details see `PEP 343 <https://www.python.org/dev/peps/pep-0343/>`_.

        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Contextmanager exit function

        Note
        ----
        For further details see `PEP 343 <https://www.python.org/dev/peps/pep-0343/>`_.

        """
        self.wait()
        self.kill()

    def close(self):
        """Function to safely close any :obj:`~pyjob.queue.Queue`
       
        Warning
        -------
        This function **must** be called if the :obj:`~pyjob.queue.Queue` is
        not used in conjunction with a Contextmanager
        
        """
        self.wait()
        self.kill()

    @abc.abstractmethod
    def kill(self):
        """Template method to kill all running jobs"""
        pass

    @abc.abstractmethod
    def submit(self):
        """Template method to submit new scripts to the :obj:`~pyjob.queue.Queue`"""
        pass

    @abc.abstractmethod
    def wait(self):
        """Template method to wait for all currently executing scripts to finish"""
        pass

    @staticmethod
    def check_script(script):
        """Check if one or more scripts are valid
        
        Parameters
        ----------
        script : str, list, tuple
           Path to one or more scripts with executable permission

        Returns
        -------
        tuple
           Path to scripts and related paths to logs

        Raises
        ------
        :exc:`~pyjob.exception.PyJobError`
           One or more scripts cannot be found or are not executable

        """
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
    def __init__(self, *args, **kwargs):
        self.queue = []
        super(ClusterQueue, self).__init__(*args, **kwargs)

    def prep_array_script(self, scripts, directory):
        """Prepare the array script for queue submission

        Parameters
        ----------
        scripts : list
           List of script paths to be executed in a single array job
        directory : str
           The directory to dump the associated script execution files in

        Returns
        -------
        tuple
           The array script and associated file containing a list of scripts

        """
        _, extension = os.path.splitext(scripts[0])
        array_jobs = NamedTemporaryFile(delete=False, dir=directory, prefix='array_', suffix='.jobs').name
        logger.debug('Writing array jobs script to %s', array_jobs)
        with open(array_jobs, 'w') as f_out:
            f_out.write(os.linesep.join(scripts) + os.linesep)
        array_script = array_jobs.replace('.jobs', '.script')
        logger.debug('Writing array master script to %s', array_script)
        content = [
            SCRIPT_HEADER, 'script=$(awk "NR==$' + self.__class__.TASK_ENV + '" ' + array_jobs + ')',
            "log=$(echo $script | sed 's/\{}/\.log/')".format(extension), '$script > $log 2>&1' + os.linesep
        ]
        with open(array_script, 'w') as f_out:
            f_out.write(os.linesep.join(content))
        return array_script, array_jobs
