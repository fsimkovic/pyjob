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
import time
import uuid

from pyjob.cexec import cexec
from pyjob.task import Task

logger = logging.getLogger(__name__)


class LoadSharingFacilityTask(Task):
    """

    Examples
    --------

    """

    ARRAY_TASK_ID = 'LSB_JOBINDEX'

    def __init__(self, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.lsf.LoadSharingFacilityTask`"""
        super(LoadSharingFacilityTask, self).__init__(*args, **kwargs)
        self.dependency = kwargs.get('dependency', [])
        self.directory = os.path.abspath(kwargs.get('directory', '.'))
        self.max_array_size = kwargs.get('max_array_size', len(self.script))
        self.name = kwargs.get('name', None)
        self.priority = kwargs.get('priority', None)
        self.queue = kwargs.get('queue', None)
        self.runtime = kwargs.get('runtime', None)
        self.shell = kwargs.get('shell', None)
        self.nprocesses = kwargs.get('processes', 1)

    @property
    def info(self):
        """:obj:`~pyjob.lsf.LoadSharingFacilityTask` information"""
        stdout = cexec(['bjobs', '-l', str(jobid)])
        if 'Done successfully' in stdout:
            return {}
        else:
            return {'job_number': self.pid, 'status': 'Running'}

    def close(self):
        """Close this :obj:`~pyjob.lsf.LoadSharingFacilityTask` after completion
       
        Warning
        -------
        It is essential to call this method if you are using any 
        :obj:`~pyjob.task.Task` without context manager.
        
        """
        self.wait()

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.lsf.LoadSharingFacilityTask`
        
        Raises
        ------
        :exc:`RuntimeError`
           Cannot delete :obj:`~pyjob.lsf.LoadSharingFacilityTask`

        """
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
        runscript = Script(directory=self.directory, prefix='lsf_', suffix='.script', stem=str(uuid.uuid1().int))
        if self.dependency:
            runscript.append('#BSUB -w %s' % ' && '.join(['deps(%s)' % str(d) for d in self.dependency]))
        if self.directory:
            runscript.append('#BSUB -cwd %s' % self.directory)
        if self.name:
            runscript.append('#BSUB -J %s' % self.name)
        if self.priority:
            runscript.append('#BSUB -sp %s' % str(self.priority))
        if self.queue:
            runscript.append('#BSUB -q %s' % self.queue)
        if self.runtime:
            runscript.append('#BSUB -W %s' % str(self.runtime))
        if self.shell:
            runscript.append('#BSUB -L %s' % self.shell)
        if self.nprocesses:
            runscript.append('#BSUB -R %s' % '"span[ptile={}]"'.format(self.nprocesses))

        if len(self.script) > 1:
            logf = runscript.path.replace('.script', '.log')
            jobsf = runscript.path.replace('.script', '.jobs')
            with open(jobsf, 'w') as f_out:
                f_out.write(os.linesep.join(self.script))

            runscript.append('#BSUB -J {}[{}-{}%{}]'.format(1, len(self.script), self.max_array_size))
            runscript.append('#BSUB -o %s' % logf)
            runscript.append('script=$(awk "NR==${}" {})'.format(LoadSharingFacilityTask.TASK_ENV, jobsf))
            runscript.append("log=$(echo $script | sed 's/\.sh/\.log/')")
            runscript.append("$script > $log 2>&1")
        else:
            runscript.append('#BSUB -o %s' % self.log[0])
            runscript.append(self.script[0])

        runscript.write()
        stdout = cexec(['bsub'], stdin=str(runscript), directory=self.directory)
        self.pid = int(stdout.split()[1][1:-1])
        logger.debug('%s [%d] submission script is %s', self.__class__.__name__, self.pid, runscript.path)
