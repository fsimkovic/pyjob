import logging
import multiprocessing
import os
import sys
import time
import uuid

from pyjob.cexec import cexec
from pyjob.task import Task

CPU_COUNT = multiprocessing.cpu_count()

logger = logging.getLogger(__name__)


class LocalTask(Task):
    """Locally executable :obj:`~pyjob.task.Task`"""

    def __init__(self, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.local.LocalTask`"""
        super().__init__(*args, **kwargs)

        self.queue = multiprocessing.Queue()
        self.kill_switch = multiprocessing.Event()
        self.processes = []
        self.chdir = kwargs.get("chdir", False)
        self.permit_nonzero = kwargs.get("permit_nonzero", False)
        self._killed = False

    @property
    def nprocesses(self):
        """Getter for the number of concurrent :obj:`~pyjob.local.LocalProcess`"""
        return self._nprocesses

    @nprocesses.setter
    def nprocesses(self, nprocesses):
        """Setter for the number of concurrent :obj:`~pyjob.local.LocalProcess`"""
        if nprocesses > CPU_COUNT:
            logger.warning("More processes requested than available CPUs")
        self._nprocesses = nprocesses

    @property
    def info(self):
        """:obj:`~pyjob.local.LocalTask` information"""
        if any(proc.is_alive() for proc in self.processes):
            return {"job_number": self.pid, "status": "Running"}
        return {}

    def close(self):
        """Close this :obj:`~pyjob.local.LocalTask` after completion"""
        if self._killed:
            return
        for proc in self.processes:
            proc.join()
        self.kill()

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.local.LocalTask`"""
        if self._killed:
            return
        if not self.kill_switch.is_set():
            self.kill_switch.set()
        # This is a requirement to avoid access to memory-inaccessible processes
        # The queue gets flushed by triggering the kill_switch
        for proc in self.processes:
            proc.join()
        for proc in self.processes:
            proc.terminate()
        logger.debug("Terminated task: %d", self.pid)
        self._killed = True

    def _run(self):
        """Method to initialise :obj:`~pyjob.local.LocalTask` execution"""
        if self._killed:
            return
        for _ in range(self.nprocesses):
            proc = LocalProcess(
                self.queue,
                self.kill_switch,
                directory=self.directory,
                chdir=self.chdir,
                permit_nonzero=self.permit_nonzero,
            )
            proc.start()
            self.processes.append(proc)
        for script in self.script:
            self.queue.put(script)
        for _ in self.processes:
            self.queue.put(None)
        self.queue.close()
        self.pid = uuid.uuid1().int
        time.sleep(0.1)


class LocalProcess(multiprocessing.Process):
    """Extension to :obj:`multiprocessing.Process` for :obj:`~pyjob.local.LocalTask`"""

    def __init__(
        self, queue, kill_switch, directory=None, permit_nonzero=False, chdir=False
    ):
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
        This object should only be instantiated by :obj:`~pyjob.local.LocalTask`!

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
            if self.chdir:
                directory = os.path.dirname(job)
            else:
                directory = self.directory
            log = os.path.splitext(job)[0] + ".log"
            with open(log, "w") as f:
                cexec(
                    [job], cwd=directory, stdout=f, permit_nonzero=self.permit_nonzero
                )
