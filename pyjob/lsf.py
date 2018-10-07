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
import time
import uuid

from pyjob.cexec import cexec
from pyjob.exception import PyJobExecutableNotFoundError
from pyjob.script import Script
from pyjob.task import ClusterTask

logger = logging.getLogger(__name__)


class LoadSharingFacilityTask(ClusterTask):
    """LoadSharingFacility (LSF) executable :obj:`~pyjob.task.Task`"""

    JOB_ARRAY_INDEX = '$LSB_JOBINDEX'
    SCRIPT_DIRECTIVE = '#BSUB'

    @property
    def info(self):
        """:obj:`~pyjob.lsf.LoadSharingFacilityTask` information"""
        if self.pid is None:
            return {}
        try:
            stdout = cexec(['bjobs', '-l', str(self.pid)], permit_nonzero=True)
        except PyJobExecutableNotFoundError:
            return {}
        if 'Done successfully' in stdout:
            return {}
        else:
            return {'job_number': self.pid, 'status': 'Running'}

    def close(self):
        """Close this :obj:`~pyjob.lsf.LoadSharingFacilityTask` after completion"""
        self.wait()

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.lsf.LoadSharingFacilityTask`

        Raises
        ------
        :exc:`RuntimeError`
           Cannot delete :obj:`~pyjob.lsf.LoadSharingFacilityTask`

        """
        if self.pid is None:
            return
        stdout = cexec(['bkill', str(self.pid)], permit_nonzero=True)
        if "is in progress" in stdout:
            stdout = cexec(['bkill', '-b', str(self.pid)], permit_nonzero=True)
            time.sleep(10)
        if any(text in stdout for text in ["has already finished", "is being terminated", "is in progress"]):
            logger.debug("Terminated task: %d", self.pid)
        else:
            raise RuntimeError('Cannot delete task!')

    def _run(self):
        """Method to initialise :obj:`~pyjob.lsf.LoadSharingFacilityTask` execution"""
        runscript = self._create_runscript()
        runscript.write()
        stdout = cexec(['bsub'], stdin=str(runscript), directory=self.directory)
        self.pid = int(stdout.split()[1][1:-1])
        logger.debug('%s [%d] submission script is %s', self.__class__.__name__, self.pid, runscript.path)

    def _create_runscript(self):
        """Utility method to create runscript"""
        runscript = Script(directory=self.directory, prefix='lsf_', suffix='.script', stem=str(uuid.uuid1().int))
        if self.dependency:
            cmd = '-w {}'.format(' && '.join(['deps(%s)' % str(d) for d in self.dependency]))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.directory:
            cmd = '-cwd {}'.format(self.directory)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.priority:
            cmd = '-sp {}'.format(self.priority)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.queue:
            cmd = '-q {}'.format(self.queue)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.runtime:
            cmd = '-W {}'.format(self.runtime)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.shell:
            cmd = '-L {}'.format(self.shell)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.nprocesses:
            cmd = '-R "span[ptile={}]"'.format(self.nprocesses)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if self.extra:
            cmd = ' '.join(map(str, self.extra))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
        if len(self.script) > 1:
            logf = runscript.path.replace('.script', '.log')
            jobsf = runscript.path.replace('.script', '.jobs')
            with open(jobsf, 'w') as f_out:
                f_out.write('\n'.join(self.script))
            cmd = '-J {}[{}-{}]%{}'.format(self.name, 1, len(self.script), self.max_array_size)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' ' + cmd)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -o {}'.format(logf))
            runscript.extend(self.get_array_bash_extension(jobsf, 1))
        else:
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -J {}'.format(self.name))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + ' -o {}'.format(self.log[0]))
            runscript.append(self.script[0])
        return runscript
