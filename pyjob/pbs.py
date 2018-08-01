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
import os
import re
import time
import uuid

from pyjob.cexec import cexec
from pyjob.task import Task

logger = logging.getLogger(__name__)


class PortableBatchSystemTask(Task):
    """PortableBatchSystem executable :obj:`~pyjob.task.Task`

    Examples
    --------

    """

    TASK_ENV = 'PBS_ARRAYID'

    def __init__(self, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.pbs.PortableBatchSystemTask`"""
        super(PortableBatchSystemTask, self).__init__(*args, **kwargs)
        self.directory = os.path.abspath(kwargs.get('directory', '.'))
        self.max_array_size = kwargs.get('max_array_size', len(self.script))
        self.name = kwargs.get('name', None)
        self.priority = kwargs.get('priority', None)
        self.queue = kwargs.get('queue', None)
        self.runtime = kwargs.get('runtime', None)
        self.shell = kwargs.get('shell', None)

    @property
    def info(self):
        """:obj:`~pyjob.pbs.PortableBatchSystemTask` information"""
        line_split1 = re.compile(":\\s+")
        line_split2 = re.compile("\\s+=\\s+")
        stdout = cexec(['qstat', '-f', str(self.pid)], permit_nonzero=True)
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

    def close(self):
        """Close this :obj:`~pyjob.pbs.PortableBatchSystemTask` after completion
        
        Warning
        -------
        It is essential to call this method if you are using any 
        :obj:`~pyjob.task.Task` without context manager.

        """
        self.wait()

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.pbs.PortableBatchSystemTask`"""
        cexec(['qdel', str(self.pid)])
        logger.debug("Terminated task: %d", self.pid)

    def _run(self):
        """Method to initialise :obj:`~pyjob.pbs.PortableBatchSystemTask` execution"""
        runscript = Script(directory=self.directory, prefix='pbs_', suffix='.script', stem=str(uuid.uuid1().int))
        runscript.append('#PBS -V')
        if self.directory:
            runscript.append('#PBS -w %s' % self.directory)
        if self.name:
            runscript.append('#PBS -N %s' % self.name)
        if self.priority:
            runscript.append('#PBS -p %s' % str(self.priority))
        if self.queue:
            runscript.append('#PBS -q %s' % self.queue)
        if self.runtime:
            m, s = divmod(self.runtime, 60)
            h, m = divmod(m, 60)
            runscript.append('#PBS -l walltime={}:{}:{}'.format(h, m, s))
        if self.shell:
            runscript.append('#PBS -S %s' % self.shell)

        if len(self.script) > 1:
            logf = runscript.path.replace('.script', '.log')
            jobsf = runscript.path.replace('.script', '.jobs')
            with open(jobsf, 'w') as f_out:
                f_out.write(os.linesep.join(self.script))

            runscript.append('#PBS -t {}-{}%{}'.format(1, len(self.script), self.max_array_size))
            runscript.append('#PBS -o %s' % logf)
            runscript.append('#PBS -e %s' % logf)
            runscript.append('script=$(awk "NR==${}" {})'.format(SunGridEngineTask.TASK_ENV, jobsf))
            runscript.append("log=$(echo $script | sed 's/\.sh/\.log/')")
            runscript.append("$script > $log 2>&1")
        else:
            runscript.append('#PBS -o %s' % self.log[0])
            runscript.append('#PBS -e %s' % self.log[0])
            runscript.append(self.script[0])

        runscript.write()
        stdout = cexec(['qsub', runscript.path], directory=self.directory)
        jobid = cexec(cmd, directory=directory)
        logger.debug('%s [%d] submission script is %s', self.__class__.__name__, self.pid, runscript.path)
