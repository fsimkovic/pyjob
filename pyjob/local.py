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

import logging
import multiprocessing
import uuid
import sys
import time

from pyjob.cexec import cexec
from pyjob.task import Task

logger = logging.getLogger(__name__)


class LocalTask(Task):
    """Locally executable :obj:`~pyjob.task.Task`

    Examples
    --------

    """

    def __init__(self, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.local.LocalTask`"""
        super(LocalTask, self).__init__(*args, **kwargs)
        self.queue = multiprocessing.Queue()
        self.kill_switch = multiprocessing.Event()
        self.processes = []
        self.nprocesses = kwargs.get('processes', 1)
        self.directory = kwargs.get('directory', '.')
        self.chdir = kwargs.get('chdir', False)
        self.permit_nonzero = kwargs.get('permit_nonzero', False)

    @property
    def info(self):
        """:obj:`~pyjob.local.LocalTask` information"""
        if any(proc.is_alive() for proc in self.processes):
            return {'job_number': self.pid, 'status': 'Running'}
        else:
            return {}

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.local.LocalTask`"""
        self.kill_switch.set()
        for proc in self.processes:
            self.queue.put(None)
        self.queue.close()
        for proc in self.processes:
            proc.terminate()
        logger.debug("Terminated task: %d", self.pid)

    def _run(self):
        """Method to initialise :obj:`~pyjob.local.LocalTask` execution"""
        for _ in range(self.nprocesses):
            proc = LocalProcess(
                self.queue,
                self.kill_switch,
                directory=self.directory,
                chdir=self.chdir,
                permit_nonzero=self.permit_nonzero)
            proc.start()
            self.processes.append(proc)
        for script in self.script:
            self.queue.put(script)
        for _ in self.processes:
            self.queue.put(None)
        self.queue.close()
        time.sleep(0.1)
        self.pid = uuid.uuid1().int


class LocalProcess(multiprocessing.Process):
    """Extension to :obj:`~multiprocessing.Process` for :obj:`~pyjob.local.LocalTask`"""

    def __init__(self,
                 queue,
                 kill_switch,
                 directory=None,
                 permit_nonzero=False,
                 chdir=False):
        """Instantiate a :obj:`~pyjob.local.LocalProcess`

        Parameters
        ----------
        queue : :obj:`~multiprocessing.Queue` 
           An instance of a :obj:`~multiprocessing.Queue`
        kill_switch : obj
           An instance of a :obj:`~multiprocessing.Event`
        directory : str, optional
           The directory to execute the jobs in
        permit_nonzero : bool, optional
           Allow non-zero return codes 

        Warning
        -------
        This object should not be instantiated by itself!

        """
        super(LocalProcess, self).__init__()
        self.queue = queue
        self.kill_switch = kill_switch
        self.directory = directory
        self.permit_nonzero = permit_nonzero
        self.chdir = chdir

    def run(self):
        """Method representing the :obj:`~pyjob.local.LocalProcess` activity"""
        for job in iter(self.queue.get, None):
            if self.kill_switch.is_set():
                continue
            else:
                if self.chdir:
                    directory = os.path.dirname(job)
                else:
                    directory = self.directory

                stdout = cexec(
                    [job],
                    directory=directory,
                    permit_nonzero=self.permit_nonzero)
                with open(job.rsplit('.', 1)[0] + '.log', 'w') as f_out:
                    f_out.write(stdout)
