# MIT License
#
# Copyright (c) 2017 Felix Simkovic
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

"""Module to store LoadSharingFacility cluster management platform code"""

__author__ = "Felix Simkovic"
__date__ = "30 May 2017"
__version__ = "0.1"

import logging
import os

from pyjob import cexec
from pyjob.platform.platform import ClusterPlatform

logger = logging.getLogger(__name__)


class LoadSharingFacility(ClusterPlatform):
    """Object to handle the Load Sharing Facility (LSF) management platform"""

    TASK_ID = "LSB_JOBINDEX"

    @staticmethod
    def hold(jobid):
        """Hold a job in the LSF queue

        Parameters
        ----------
        jobid : int
           The job id to remove

        """
        cexec(["bstop", str(jobid)])
        logger.debug("Holding back job %d from the queue", jobid)

    @staticmethod
    def kill(jobid):
        """Remove a job from the LSF queue
        
        Parameters
        ----------
        jobid : int
           The job id to remove

        Raises
        ------
        RuntimeError
           Execution exited with non-zero return code

        """
        stdout = cexec(["bkill", str(jobid)], permit_nonzero=True)
        # Large arrays can take time to be full deleted, give it a few moments
        if "is in progress" in stdout:
            stdout = cexec(["bkill", "-b", str(jobid)], permit_nonzero=True)
            import time
            time.sleep(10)
        if any(text in stdout for text in ["has already finished", "is being terminated", "is in progress"]):
            logger.debug("Removed job %d from the queue", jobid)
        else:
            msg = "Execution of '{0}' exited with non-zero return code: {1}".format("bkill " + str(jobid), stdout)
            raise RuntimeError(msg)

    @staticmethod
    def rls(jobid):
        """Release a job from the LSF queue

        Parameters
        ----------
        jobid : int
           The job id to remove

        """
        cexec(["bresume", str(jobid)])
        logger.debug("Released job %d from the queue", jobid)

    @staticmethod
    def stat(jobid):
        """Obtain information about a job id

        Parameters
        ----------
        jobid : int
           The job id to remove

        Returns
        -------
        dict
           A dictionary with job specific data

        Todo
        ----
        * Extract the correct information

        """
        stdout = cexec(["bjobs", "-l", str(jobid)])
        if "Done successfully" in stdout:
            return {}
        else:
            return {'job_number': jobid, 'status': "Running"}

    @staticmethod
    def sub(command, array=None, deps=None, directory=None, hold=False, log=None, name=None, priority=None,
            queue=None, runtime=None, shell=None, threads=None, *args, **kwargs):
        """Submit a job to the LSF queue

        Parameters
        ----------
        command : list
           A list with the final command
        array : list, optional
           A list of array instructions in form of [min, max, (step)].
           ``step`` is optional.
        deps : list, optional
           A list of dependency job ids
        directory : str, optional
           A path to a directory to run the job in
        hold : bool, optional
           Submit but __hold__ the job
        log : str, optional
           The path to a logfile for stdout
        name : str, optional
           The name of the job
        pe_opts : list, optional
           Job-specific keywords [Unused]
        priority : int, optional
           The priority level of the job
        queue : str, optional
           The queue to submit the job to
        runtime : int, optional
           The maximum runtime of the job in seconds
        shell : str, optional
           The absolute path to the shell to run the job in
        threads : int, optional
           The maximum number of threads available to a job

        """
        cmd = ["bsub", "-cwd", directory if directory else os.getcwd()]
        if array:
            name = "pyjob" if name is None else name
            if len(array) == 3:
                cmd += ["-J", "{0}[{1}-{2}%{3}]".format(name, array[0], array[1], array[2])]
            elif len(array) == 2:
                cmd += ["-J", "{0}[{1}-{2}]".format(name, array[0], array[1])]
            name = None             # Reset this!
        if deps:
            cmd += ["-w", " && ".join(["done(%s)" % dep for dep in map(str, deps)])]
        if hold:
            cmd += ["-H"]
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
        command_f = command[0] if isinstance(command, list) else command
        stdout = cexec(cmd, stdin=open(command_f).read(), directory=directory)
        jobid = int(stdout.split()[1][1:-1])
        logger.debug("Job %d successfully submitted to the LSF queue", jobid)
        return jobid
