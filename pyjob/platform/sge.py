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

"""Module to store SunGridEngine cluster management platform code"""

__author__ = "Felix Simkovic"
__date__ = "24 May 2017"
__version__ = "0.2"

import logging
import os
import re

from pyjob import cexec
from pyjob.platform.platform import ClusterPlatform

logger = logging.getLogger(__name__)


class SunGridEngine(ClusterPlatform):
    """Object to handle the Sun Grid Engine (SGE) management platform"""

    TASK_ID = "SGE_TASK_ID"

    @staticmethod
    def alt(jobid, priority=None):
        """Alter a job in the SGE queue
        
        Parameters
        ----------
        jobid : int
           The job id to remove
        priority : int, optional
           The priority level of the job

        Notes
        -----
        This function is currently still under development does not provide
        the full range of ``qalter`` flags.

        Todo
        ----
        * Add more functionality
        * Add better debug message to include changed options

        """
        cmd = ["qalter"]
        if priority:
            cmd += ["-p", str(priority)]
        cmd += [str(jobid)]
        cexec(cmd)
        logger.debug("Altered parameters for job %d in the queue", jobid)

    @staticmethod
    def hold(jobid):
        """Hold a job in the SGE queue

        Parameters
        ----------
        jobid : int
           The job id to remove

        """
        cexec(["qhold", str(jobid)])
        logger.debug("Holding back job %d from the queue", jobid)

    @staticmethod
    def kill(jobid):
        """Remove a job from the SGE queue
        
        Parameters
        ----------
        jobid : int
           The job id to remove
        
        """
        cexec(["qdel", str(jobid)])
        logger.debug("Removed job %d from the queue", jobid)

    @staticmethod
    def rls(jobid):
        """Release a job from the SGE queue
        
        Parameters
        ----------
        jobid : int
           The job id to remove

        """
        cexec(["qrls", str(jobid)])
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

        """
        stdout = cexec(["qstat", "-j", str(jobid)], permit_nonzero=True)
        data = {}
        line_split = re.compile(":\s+")
        for line in stdout.split(os.linesep):
            line = line.strip()
            if 'jobs do not exist' in line:
                return data
            if not line or "=" * 30 in line:
                continue
            else:
                kv = line_split.split(line, 1)
                if len(kv) == 2:
                    data[kv[0]] = kv[1]
        return data

    @staticmethod
    def sub(command, array=None, deps=None, directory=None, hold=False, log=None, name=None, pe_opts=None,
            priority=None, queue=None, runtime=None, shell=None, threads=None, *args, **kwargs):
        """Submit a job to the SGE queue

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
           Job-specific keywords
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
        cmd = ["qsub", "-cwd", "-V", "-w", "e", "-j", "y"]
        if array and len(array) == 3:
            cmd += ["-t", "{0}-{1}".format(array[0], array[1]), "-tc", str(array[2])]
        elif array and len(array) == 2:
            cmd += ["-t", "{0}-{1}".format(array[0], array[1])]
        if deps:
            cmd += ["-hold_jid", "{0}".format(",".join(map(str, deps)))]
        if hold:
            cmd += ["-h"]
        if log:
            cmd += ["-o", log]
        if name:
            cmd += ["-N", name]
        if pe_opts:
            cmd += ["-pe"] + pe_opts.split()
        if priority:
            cmd += ["-p", str(priority)]
        if queue:
            cmd += ["-q", queue]
        if runtime:
            cmd += ["-l", "h_rt={0}".format(runtime)]
        if shell:
            cmd += ["-S", shell]
        if threads:
            cmd += ["-pe mpi", str(threads)]
        cmd += command if isinstance(command, list) else [command]
        stdout = cexec(cmd, directory=directory)
        jobid = int(stdout.split()[2].split(".")[0]) if array else int(stdout.split()[2])
        logger.debug("Job %d successfully submitted to the SGE queue", jobid)
        return jobid
