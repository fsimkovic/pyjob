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
import uuid

from pyjob.cexec import cexec
from pyjob.script import Script
from pyjob.task import Task

logger = logging.getLogger(__name__)


class SunGridEngineTask(Task):
    """SunGridEngine executable :obj:`~pyjob.task.Task`

    Examples
    --------

    """

    TASK_ENV = 'SGE_TASK_ID'

    def __init__(self, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.sge.SunGridEngineTask`"""
        super(SunGridEngineTask, self).__init__(*args, **kwargs)
        self.dependency = kwargs.get('dependency', [])
        self.directory = os.path.abspath(kwargs.get('directory', '.'))
        self.max_array_size = kwargs.get('max_array_size', len(self.script))
        self.name = kwargs.get('name', None)
        self.pe_opts = kwargs.get('pe_opts', [])
        self.priority = kwargs.get('priority', None)
        self.queue = kwargs.get('queue', None)
        self.runtime = kwargs.get('runtime', None)
        self.shell = kwargs.get('shell', None)
        self.nprocesses = kwargs.get('nprocesses', 1)

    @property
    def info(self):
        """:obj:`~pyjob.sge.SunGridEngineTask` information"""
        stdout = cexec(["qstat", "-j", str(self.pid)], permit_nonzero=True)
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

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.sge.SunGridEngineTask`"""
        cexec(['qdel', str(self.pid)])
        logger.debug("Terminated task: %d", self.pid)

    def _run(self):
        """Method to initialise :obj:`~pyjob.sge.SunGridEngineTask` execution"""
        runscript = Script(
            directory=self.directory,
            prefix='sge_',
            suffix='.script',
            stem=str(uuid.uuid1().int))
        runscript.append('#$ -V')
        runscript.append('#$ -w e')
        runscript.append('#$ -j y')
        if self.dependency:
            runscript.append(
                '#$ -hold_jid %s' % ','.join(map(str, self.dependency)))
        if self.name:
            runscript.append('#$ -N %s' % self.name)
        if self.pe_opts:
            runscript.append('#$ -pe %s' % ' '.join(map(str, self.pe_opts)))
        if self.priority:
            runscript.append('#$ -p %s' % str(self.priority))
        if self.queue:
            runscript.append('#$ -q %s' % self.queue)
        if self.runtime:
            runscript.append('#$ -l h_rt=%s' % str(self.runtime))
        if self.shell:
            runscript.append('#$ -S %s' % self.shell)
        if self.nprocesses:
            runscript.append('#$ -pe mpi %d' % self.nprocesses)
        if self.directory:
            runscript.append('#$ -wd %s' % self.directory)
        else:
            runscript.append('#$ -cwd')

        if len(self.script) > 1:
            logf = runscript.path.replace('.script', '.log')
            jobsf = runscript.path.replace('.script', '.jobs')
            with open(jobsf, 'w') as f_out:
                f_out.write(os.linesep.join(self.script))

            runscript.append('#$ -t %d-%d -tc %d' % (1, len(self.script),
                                                     self.max_array_size))
            runscript.append('#$ -o %s' % logf)
            runscript.append('script=$(awk "NR==${}" {})'.format(
                SunGridEngineTask.TASK_ENV, jobsf))
            runscript.append("log=$(echo $script | sed 's/\.sh/\.log/')")
            runscript.append("$script > $log 2>&1")
        else:
            runscript.append('#$ -o %s' % self.log[0])
            runscript.append(self.script[0])

        runscript.write()
        stdout = cexec(['qsub', runscript.path], directory=self.directory)
        if len(self.script) > 1:
            self.pid = int(stdout.split()[2].split(".")[0])
        else:
            self.pid = int(stdout.split()[2])
        logger.debug('%s [%d] submission script is %s',
                     self.__class__.__name__, self.pid, runscript.path)
