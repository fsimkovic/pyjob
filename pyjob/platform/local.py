"""Module to store local job management code"""

__author__ = "Felix Simkovic"
__date__ = "09 May 2017"
__version__ = "0.1"

import logging
import multiprocessing
import time

from pyjob import cexec
from pyjob.platform.platform import Platform

logger = logging.getLogger(__name__)


class _Worker(multiprocessing.Process):
    """Simple manual worker class to execute jobs in the queue"""

    def __init__(self, queue, directory=None, permit_nonzero=False):
        """Instantiate a new worker

        Parameters
        ----------
        queue : obj
           An instance of a :obj:`Queue <multiprocessing.Queue>`
        directory : str, optional
           The directory to execute the jobs in
        permit_nonzero : bool, optional
           Allow non-zero return codes [default: False]

        """
        super(_Worker, self).__init__()
        self.directory = directory
        self.permit_nonzero = permit_nonzero
        self.queue = queue

    def run(self):
        """Method representing the process's activity"""
        for job in iter(self.queue.get, None):
            stdout = cexec([job], directory=self.directory, permit_nonzero=self.permit_nonzero)
            with open(job.rsplit('.', 1)[0] + '.log', 'w') as f_out:
                f_out.write(stdout)
 

# Store a reference to the Workers
WORKERS = None


class LocalJobServer(Platform):
    """A local server to execute jobs via the multiprocessing module
    
    Examples
    --------

    The most basic example of a :obj:`LocalJobServer` is to run scripts across one or
    more processors on a local machine. This can be achieved with the following example.

    >>> from pyjob.misc import make_python_script
    >>> from pyjob.platform import LocalJobServer
    >>> scripts = [
    ...     make_python_script(["import sys;", "print('hello');", "sys.exit(0);"])
    ...     for _ in range(3)
    ... ]
    >>> LocalJobServer.sub(scripts, nproc=2)

    This will create three Python script files and execute them by calling :func:`sub <LocalJobServer.sub>`.
    
    Sometimes you might want to submit many jobs where you know that some are going to fail. In this 
    case, you can also use the :obj:`LocalJobServer` and provide the ``permit_nonzero`` keyword argument,
    which will allow non-zero return codes from commands.

    """

    @staticmethod
    def kill(jobid):
        """Remove a job from the local process list
        
        Parameters
        ----------
        jobid : int
           The job id to remove
        
        """
        if WORKERS:
            for wk in WORKERS:
                if wk.is_alive():
                    wk.terminate()
            logger.debug("Terminated job %d", jobid)
        else:
            logger.debug("Job %d not in queue", jobid)

    @staticmethod
    def stat(jobid):
        """Obtain information about a job id
        
        Parameters
        ----------
        jobid : int
           The job id to remove
        
        """
        if WORKERS and any(wk.is_alive() for wk in WORKERS):
            return {'job_number': jobid, 'status': "Running"}
        else:
            return {}

    @staticmethod
    def sub(command, directory=None, nproc=1, permit_nonzero=False, *args, **kwargs):
        """Submission function for local job submission via ``multiprocessing``
        
        Parameters
        ----------
        command : list
           A list with the final command
        directory : str, optional
           The directory to execute the jobs in
        nproc : int, optional
           The number of processors to use
        permit_nonzero : bool, optional
           Allow non-zero return codes [default: False]
        runtime : int, optional
           The maximum runtime of the job in seconds

        """
        # Create a new queue
        queue = multiprocessing.Queue()
        
        # Create workers equivalent to the number of jobs
        global WORKERS
        WORKERS = workers = []
        for _ in range(nproc):
            wp = _Worker(queue, directory=directory, permit_nonzero=permit_nonzero)
            wp.start()
            workers.append(wp)
        # Add each command to the queue
        for cmd in command:
            queue.put(cmd)
        # Stop workers from exiting without completion
        for _ in range(nproc):
            queue.put(None)
        # Disallow addition of further jobs
        queue.close()
        # Need this in case we kill the job immediately after submitting
        time.sleep(0.1)
        return queue._opid
