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

import abc
import logging
import os
import time
import warnings

from pyjob import config
from pyjob.exception import PyJobError, PyJobTaskLockedError
from pyjob.script import ScriptCollector, is_valid_script_path

ABC = abc.ABCMeta('ABC', (object, ), {})
logger = logging.getLogger(__name__)


class Task(ABC):
    """Abstract base class for executable tasks"""

    def __init__(self, script, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.task.Task`

        Parameters
        ----------
        script : :obj:`~pyjob.script.ScriptCollector`, :obj:`~pyjob.script.Script`, str, list, tuple
           A :obj:`str`, :obj:`list` or :obj:`tuple` of one or more script paths

        """
        self.pid = None
        self.locked = False
        if isinstance(script, ScriptCollector):
            self.script_collector = script
        else:
            self.script_collector = ScriptCollector(script)
        # These arguments are universal to all Task entities
        self.directory = os.path.abspath(kwargs.get('directory') or config.get('directory') or '.')
        self.nprocesses = kwargs.get('processes') or config.get('processes') or 1

    def __del__(self):
        """Exit function at instance deletion"""
        if not self.locked:
            self.lock()
        self.close()

    def __enter__(self):
        """Contextmanager entry function

        Note
        ----
        For further details see `PEP 343 <https://www.python.org/dev/peps/pep-0343/>`_.

        """
        return self

    def __exit__(self, *exc):
        """Contextmanager exit function

        Note
        ----
        For further details see `PEP 343 <https://www.python.org/dev/peps/pep-0343/>`_.

        """
        if not self.locked:
            self.lock()
        self.close()

    def __repr__(self):
        """Representation of the :obj:`~pyjob.task.Task`"""
        return '{}(pid={})'.format(self.__class__.__name__, self.pid)

    # ------------------ Abstract methods and properties ------------------

    @abc.abstractproperty
    def info(self):    # pragma: no cover
        """Abstract property to provide info about the :obj:`~pyjob.task.Task`"""
        pass

    @abc.abstractmethod
    def close(self):    # pragma: no cover
        """Abstract method to end :obj:`~pyjob.task.Task`"""
        pass

    @abc.abstractmethod
    def kill(self):    # pragma: no cover
        """Abstract method to forcefully terminate :obj:`~pyjob.task.Task`"""
        pass

    @abc.abstractmethod
    def _run(self):    # pragma: no cover
        """Abstract property to start execution of the :obj:`~pyjob.task.Task`"""
        pass

    # ------------------ Other task-specific general methods ------------------

    @property
    def completed(self):
        """Boolean to indicate :obj:`~pyjob.task.Task` completion"""
        return self.locked and not bool(self.info)

    @property
    def log(self):
        """The log file path"""
        return [script.log for script in self.script_collector]

    @property
    def script(self):
        """The script file path"""
        return [script.path for script in self.script_collector]

    def add_script(self, script):
        """Add further scripts to this :obj:`~pyjob.task.Task`

        Parameters
        ----------
        script : :obj:`~pyjob.script.Script`, str, list, tuple
           Something representing one or more scripts

        """
        if self.locked:
            raise PyJobTaskLockedError('This task is locked!')
        self.script_collector.add(script)

    def lock(self):
        """Lock this :obj:`~pyjob.task.Task`"""
        self.locked = True
        logger.debug('Locked %s [%d]', self.__class__.__name__, self.pid)

    def run(self):
        """Start the execution of this :obj:`~pyjob.task.Task`

        Raises
        ------
        :exc:`~pyjob.exception.PyJobError`
           One or more executable scripts required prior to execution
        :exc:`~pyjob.exception.PyJobTaskLockedError`
           Locked task, cannot restart or rerun

        """
        if self.locked:
            raise PyJobTaskLockedError('This task is locked!')
        if len(self.script_collector) < 1:
            raise PyJobError('One or more executable scripts required prior to execution')
        self.script_collector.dump()
        self._run()
        logger.debug('Started execution of %s [%d]', self.__class__.__name__, self.pid)
        self.lock()

    def wait(self, interval=30, monitor_f=None, success_f=None, check_success=None, monitor=None):
        """Method to wait for the completion of the current :obj:`~pyjob.task.Task`

        Parameters
        ----------
        interval : int, optional
           The interval to wait between checking (in seconds)
        monitor_f : func, optional
           A :obj:`callable` that is regularly invoked
        success_f : func, optional
           A :obj:`callable` to check for early termination of :obj:`~pyjob.task.Task`

        Note
        ----
        The `success_f` argument needs to accept a log file as input and return
        a :obj:`bool`.

        """
        if check_success:
            warnings.warn('This keyword argument has been deprecated, use success_f instead', DeprecationWarning)
            success_f = check_success

        if monitor:
            warnings.warn('This keyword argument has been deprecated, use monitor_f instead', DeprecationWarning)
            monitor_f = monitor

        def callable_checker(f):
            return bool(f and callable(f))

        do_check_success = callable_checker(success_f)
        if do_check_success:
            msg = 'Checking for %s %d success with function %s'
            logger.debug(msg, self.__class__.__name__, self.pid, success_f.__name__)
        do_monitor = callable_checker(monitor_f)
        while not self.completed:
            if do_check_success:
                for log in self.log:
                    if os.path.isfile(log) and success_f(log):
                        logger.debug("%s %d succeeded, run log: %s", self.__class__.__name__, self.pid, log)
                        self.kill()
            if do_monitor:
                monitor_f()
            time.sleep(interval)


class ClusterTask(Task):
    """Abstract base class for executable cluster tasks"""

    def __init__(self, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.task.ClusterTask`"""
        super(ClusterTask, self).__init__(*args, **kwargs)
        self.dependency = kwargs.get('dependency', [])
        self.max_array_size = kwargs.get('max_array_size') or config.get('max_array_size') or len(self.script)
        self.priority = kwargs.get('priority', None)
        self.queue = kwargs.get('queue') or config.get('queue')
        self.runtime = kwargs.get('runtime') or config.get('runtime')
        self.shell = kwargs.get('shell') or config.get('shell')
        self.name = kwargs.get('name') or config.get('name') or 'pyjob'
        self.extra = kwargs.get('extra', [])

    @abc.abstractmethod
    def _create_runscript(self):
        """Utility method to create a :obj:`~pyjob.task.ClusterTask` runscript"""
        pass

    def get_array_bash_extension(self, jobsf, offset):
        """Get the array job bash extension for the ``runscript``

        Parameters
        ----------
        jobsf : str
           The file containing all scripts on a per-line basis
        offset : int
           The offset to be applied to the ``JOB_ARRAY_INDEX``

        Returns
        -------
        list
           A list of lines to be written to the ``runscript``

        Raises
        ------
        :exc:`ValueError`
           Invalid offset
        :exc:`ValueError`
           Valid job file required

        """
        if jobsf is None or not os.path.isfile(jobsf):
            raise ValueError('Valid job file required')
        if offset < 0:
            raise ValueError('Invalid offset')
        if offset > 0:
            script_def = 'script=$(awk "NR==$(({} + {}))" {})'.format(self.__class__.JOB_ARRAY_INDEX, offset, jobsf)
        else:
            script_def = 'script=$(awk "NR=={}" {})'.format(self.__class__.JOB_ARRAY_INDEX, jobsf)
        return [script_def, 'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")', '$script > $log 2>&1']
