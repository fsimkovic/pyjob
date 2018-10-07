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
import re
import time
import uuid

from pyjob.cexec import cexec
from pyjob.exception import PyJobExecutableNotFoundError
from pyjob.script import Script
from pyjob.task import ClusterTask

logger = logging.getLogger(__name__)

RE_LINE_SPLIT_1 = re.compile(":\\s+")
RE_LINE_SPLIT_2 = re.compile("\\s+=\\s+")


class PortableBatchSystemTask(ClusterTask):
    """PortableBatchSystem executable :obj:`~pyjob.task.Task`"""

    JOB_ARRAY_INDEX = '$PBS_ARRAYID'
    SCRIPT_DIRECTIVE = '#PBS'

    @property
    def info(self):
        """:obj:`~pyjob.pbs.PortableBatchSystemTask` information"""
        if self.pid is None:
            return {}
        try:
            stdout = cexec(['qstat', '-f', str(self.pid)], permit_nonzero=True)
        except PyJobExecutableNotFoundError:
            return {}
        all_lines = stdout.splitlines()
        data = {}
        key, job_id = RE_LINE_SPLIT_1.split(all_lines[0], 1)
        data[key] = job_id
        for line in all_lines[1:]:
            line = line.strip()
            if 'Unknown queue destination' in line:
                return data
            else:
                kv = RE_LINE_SPLIT_2.split(line, 1)
                if len(kv) == 2:
                    data[kv[0]] = kv[1]
        return data

    def close(self):
        """Close this :obj:`~pyjob.pbs.PortableBatchSystemTask` after completion"""
        self.wait()

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.pbs.PortableBatchSystemTask`"""
        if self.pid is None:
            return
        cexec(['qdel', str(self.pid)])
        logger.debug("Terminated task: %d", self.pid)

    def _run(self):
        """Method to initialise :obj:`~pyjob.pbs.PortableBatchSystemTask` execution"""
        runscript = self._create_runscript()
        runscript.write()
        self.pid = cexec(['qsub', runscript.path], directory=self.directory)
        logger.debug('%s [%d] submission script is %s', self.__class__.__name__, self.pid, runscript.path)

    def _create_runscript(self):
        """Utility method to create runscript"""
        runscript = Script(directory=self.directory, prefix='pbs_', suffix='.script', stem=str(uuid.uuid1().int))
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -V')
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -N {}'.format(self.name))
        if self.directory:
            cmd = '-w {}'.format(self.directory)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.priority:
            cmd = '-p {}'.format(self.priority)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.queue:
            cmd = '-q {}'.format(self.queue)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.runtime:
            h, m = divmod(self.runtime, 60)
            m, s = divmod(m, 60)
            cmd = '-l walltime={}:{}:{}'.format(h, m, s)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.shell:
            cmd = '-S {}'.format(self.shell)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.nprocesses:
            cmd = '-n {}'.format(self.nprocesses)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.extra:
            cmd = ' '.join(map(str, self.extra))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if len(self.script) > 1:
            logf = runscript.path.replace('.script', '.log')
            jobsf = runscript.path.replace('.script', '.jobs')
            with open(jobsf, 'w') as f_out:
                f_out.write('\n'.join(self.script))
            cmd = '-t {}-{}%{}'.format(1, len(self.script), self.max_array_size)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -o {}'.format(logf))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -e {}'.format(logf))
            runscript.extend(self.get_array_bash_extension(jobsf, 0))
        else:
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -o {}'.format(self.log[0]))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -e {}'.format(self.log[0]))
            runscript.append(self.script[0])
        return runscript
