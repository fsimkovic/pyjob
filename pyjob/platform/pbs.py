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

"""Module to store PortableBatchSystem cluster management platform code"""

__author__ = "Felix Simkovic"
__date__ = "29 Sep 2017"
__version__ = "0.1"

import logging
import os
import re

from pyjob import cexec
from pyjob.platform.platform import ClusterPlatform

logger = logging.getLogger(__name__)


class PortableBatchSystem(ClusterPlatform):
    """Object to handle the PortableBatchSystem (PBS) management platform"""

    ARRAY_TASK_ID = "PBS_ARRAYID"

    @staticmethod
    def alt(jobid, priority=None):
        """Alter a job in the PBS queue
        
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

        """
        cmd = ["qalter"]
        if priority:
            cmd += ["-p", str(priority)]
            logger.debug("Altered priority for job %s by %s",
                         str(jobid), str(priority))
        cmd += [str(jobid)]
        cexec(cmd)

    @staticmethod
    def hold(jobid):
        """Hold a job in the PBS queue

        Parameters
        ----------
        jobid : int
           The job id to remove

        """
        cexec(["qhold", str(jobid)])
        logger.debug("Holding back job %d from the queue", jobid)

    @staticmethod
    def kill(jobid):
        """Remove a job from the PBS queue
        
        Parameters
        ----------
        jobid : int
           The job id to remove
        
        """
        cexec(["qdel", str(jobid)])
        logger.debug("Removed job %d from the queue", jobid)

    @staticmethod
    def rls(jobid):
        """Release a job from the PBS queue
        
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
        line_split1 = re.compile(":\s+")
        line_split2 = re.compile("\s+=\s+")

        stdout = cexec(["qstat", "-f", str(jobid)], permit_nonzero=True)
        all_lines = stdout.split(os.linesep)

        data = {}
        key, job_id = line_split1.split(all_lines[0], 1)
        data[key] = job_id

        for line in all_lines[1:]:
            line = line.strip()
            if 'Unknown queue destination' in line:
                return data
            else:
                kv = line_split2.split(line, 1)
                if len(kv) == 2:
                    data[kv[0]] = kv[1]
        return data

    @staticmethod
    def sub(command, array=None, directory=None, hold=False, log=None, name=None,
            priority=None, queue=None, runtime=None, shell=None, *args, **kwargs):
        """Submit a job to the PBS queue

        Parameters
        ----------
        command : list
           A list with the final command
        array : list, optional
           A list of array instructions in form of [min, max, (step)].
           ``step`` is optional.
        directory : str, optional
           A path to a directory to run the job in
        hold : bool, optional
           Submit but __hold__ the job
        log : str, optional
           The path to a logfile for stdout
        name : str, optional
           The name of the job
        priority : int, optional
           The priority level of the job
        queue : str, optional
           The queue to submit the job to
        runtime : int, optional
           The maximum runtime of the job in seconds
        shell : str, optional
           The absolute path to the shell to run the job in

        """
        cmd = ["qsub", "-w", os.environ["PWD"], "-V"]
        if array and len(array) == 3:
            cmd += ["-t", "{}-{}%{}".format(array[0], array[1], array[2])]
        elif array and len(array) == 2:
            cmd += ["-t", "{}-{}".format(array[0], array[1])]
        if hold:
            cmd += ["-h"]
        if log:
            cmd += ["-o", log]
            cmd += ["-e", log]
        if name:
            cmd += ["-N", name]
        if priority:
            cmd += ["-p", str(priority)]
        if queue:
            cmd += ["-q", queue]
        if runtime:
            m, s = divmod(runtime, 60)
            h, m = divmod(m, 60)
            cmd += ["-l", "walltime={}:{}:{}".format(h, m, s)]
        if shell:
            cmd += ["-S", shell]
        cmd += command if isinstance(command, list) else [command]
        jobid = cexec(cmd, directory=directory)
        logger.debug("Job %d successfully submitted to the PBS queue", jobid)
        return jobid
