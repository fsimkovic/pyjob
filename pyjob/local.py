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

from multiprocessing import Event as MpEvent
from multiprocessing import Process as MpProcess
from multiprocessing import Queue as MpQueue
from time import sleep

import logging
import os
import uuid

from pyjob.cexec import cexec
from pyjob.queue import Queue

logger = logging.getLogger(__name__)



class LocalJobServer(Queue):

    def __init__(self, processes=1):
        super(LocalJobServer, self).__init__()
        self.pid = uuid.uuid1()
        self.nprocesses = processes
        self.processes = Processes(processes=self.nprocesses)

    def kill(self):
        self.processes.terminate()
        self.processes.queue.close()

    def submit(self, command):
        if isinstance(command, str):
            command = [command]
        logger.debug('Submitting %d new job(s)', len(command))
        for cmd in command:
            self.processes.queue.put(cmd)
        sleep(0.1)

    def wait(self, timeout=None):
        self.processes.join(timeout=timeout)
        self.processes.terminate()
        self.processes = Processes(processes=self.nprocesses)


class Processes(object):

    def __init__(self, processes=1):
        self.nprocesses = processes
        self.queue = MpQueue()
        self.kill_switch = MpEvent()
        self._processes = []
        for _ in range(self.nprocesses):
            process = Process(self.queue, self.kill_switch)
            process.start()
            self._processes.append(process)

    def join(self, timeout=None):
        for _ in self._processes:
            self.queue.put(None)
        sleep(0.1)
        for proc in self._processes:
            proc.join(timeout)

    def terminate(self):
        self.kill_switch.set()
        for proc in self._processes:
            proc.terminate()


class Process(MpProcess):
    
    def __init__(self, queue, kill_switch, directory='.', chdir=False, permit_nonzero=False):
        super(Process, self).__init__()
        self.queue = queue
        self.kill_switch = kill_switch
        self.directory = directory
        self.permit_nonzero = permit_nonzero
        self.chdir = chdir
        self.idle = True

    def run(self):
        for job in iter(self.queue.get, None):
            if self.kill_switch.is_set():
                continue
            directory = os.path.dirname(job) if self.chdir else self.directory
            stdout = cexec([job], directory=directory, permit_nonzero=self.permit_nonzero)
            with open(job.rsplit('.', 1)[0] + '.log', 'w') as f_out:
                f_out.write(stdout)
