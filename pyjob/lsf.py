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

from time import sleep

import logging
import os

from pyjob.cexec import cexec
from pyjob.queue import ClusterQueue

logger = logging.getLogger(__name__)


class LoadSharingFacility(ClusterQueue):
    """

    Examples
    --------

    The recommended way to use a :obj:`~pyjob.queue.Queue` is by
    creating a context and perform all actions within. The context will
    not be left until all submitted scripts have executed.

    >>> with LoadSharingFacility() as queue:
    ...     queue.submit(['script1.py', 'script2.sh', 'script3.pl'])
    
    A :obj:`~pyjob.queue.Queue` instance can also be assigned to a
    variable and used throughout. However, it is required to close the 
    :obj:`~pyjob.queue.Queue` explicitly.

    >>> queue = LoadSharingFacility()
    >>> queue.submit(['script1.py', 'script2.sh', 'script3.pl'])
    >>> queue.close()

    """

    ARRAY_TASK_ID = 'LSB_JOBINDEX'

    def __init__(self, *args, **kwargs):
        super(LoadSharingFacility, self).__init__(*args, **kwargs)

    def kill(self):
        if len(self.queue) > 0:
            cmd = ['bkill', str(jobid)]
            stdout = cexec(cmd, permit_nonzero=True)
            if "is in progress" in stdout:
                stdout = cexec(['bkill', '-b', str(jobid)], permit_nonzero=True)
                sleep(10)
            if any(text in stdout for text in ["has already finished", "is being terminated", "is in progress"]):
                self.queue = []
            else:
                raise RuntimeError('Cannot delete jobs from %s!' % self.__class__.__name__)

    def submit(self,
               script,
               array=None,
               deps=None,
               hold=False,
               log=None,
               name=None,
               priority=None,
               queue=None,
               runtime=None,
               shell=None,
               threads=None):

        script, log = self.__class__.check_script(script)
        nscripts = len(script)

        if nscripts > 1:
            master, _ = self.prep_array_script(script, '.')
            script = [master]
            log = [os.devnull]
            shell = '/bin/sh'
            if array is None:
                array = [1, nscripts, nscripts]

        cmd = ['bsub', '-cwd', os.getcwd()]
        if array:
            name = "pyjob" if name is None else name
            if len(array) == 3:
                cmd += ["-J", "{0}[{1}-{2}%{3}]".format(name, array[0], array[1], array[2])]
            elif len(array) == 2:
                cmd += ["-J", "{0}[{1}-{2}]".format(name, array[0], array[1])]
            name = None  # Reset this!
        if deps:
            cmd += ["-w", " && ".join(["done(%s)" % dep for dep in map(str, deps)])]
        if log:
            cmd += ["-o", log]
        if name:
            cmd += ["-J", '"{0}"'.format(name)]
        if priority:
            cmd += ["-sp", str(priority)]
        if queue:
            cmd += ["-q", queue]
        if shell:
            cmd += ["-L", shell]
        if threads:
            cmd += ["-R", '"span[ptile={0}]"'.format(threads)]
        if runtime:

            cmd += ["-W", str(runtime)]
        stdout = cexec(cmd, stdin=open(script[0]).read())
        jobid = int(stdout.split()[1][1:-1])
        self.queue.append(jobid)

    def wait(self):
        while len(self.queue) > 0:
            i = len(self.queue)
            while i > 0:
                cmd = ['bjobs', '-l', str(self.queue[i - 1])]
                stdout = cexec(cmd)
                if "Done successfully" in stdout:
                    self.queue.pop(i - 1)
                i -= 1
            sleep(5)
