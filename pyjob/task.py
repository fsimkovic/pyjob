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

from pyjob.exception import PyJobError
from pyjob.script import ScriptContainer, is_valid_script_path

ABC = abc.ABCMeta('ABC', (object, ), {})
logger = logging.getLogger(__name__)


class Task(ABC):
    """Abstract base class for executable tasks"""

    def __init__(self, script, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.task.Task`

        Parameters
        ----------
        script : str, list, tuple
           A :obj:`str`, :obj:`list` or :obj:`tuple` of one or more script paths

        """
        self.pid = None
        self.locked = False
        self.script_container = ScriptContainer(script)
        # These arguments are universal to all Task entities
        self.directory = os.path.abspath(kwargs.get('directory', '.'))
        self.nprocesses = kwargs.get('processes', 1)

    def __del__(self):
        """Exit function at instance deletion"""
        if not self.locked:
            self.locked = True
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
            self.locked = True
        self.close()

    def __repr__(self):
        """Representation of the :obj:`~pyjob.task.Task`"""
        return '{}(pid={})'.format(self.__class__.__name__, self.pid)

    # ------------------ Abstract methods and properties ------------------

    @abc.abstractproperty
    def info(self):  # pragma: no cover
        """Abstract property to provide info about the :obj:`~pyjob.task.Task`"""
        pass

    @abc.abstractmethod
    def close(self):  # pragma: no cover
        """Abstract method to end :obj:`~pyjob.task.Task`"""
        pass

    @abc.abstractmethod
    def kill(self):  # pragma: no cover
        """Abstract method to forcefully terminate :obj:`~pyjob.task.Task`"""
        pass

    @abc.abstractmethod
    def _run(self):  # pragma: no cover
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
        return [script.rsplit('.', 1)[0] + '.log' for script in self.script]

    @property
    def script(self):
        """The script file path"""
        return [script.path for script in self.script_container]

    def add_script(self, script):
        """Add further scripts to this :obj:`~pyjob.task.Task`

        Parameters
        ----------
        script : :obj:`~pyjob.script.Script`, str, list, tuple
           Something representing one or more scripts

        """
        self.script_container.add(script)

    def run(self):
        """Start the execution of this :obj:`~pyjob.sge.SunGridEngineTask`

        Raises
        ------
        :exc:`~pyjob.exception.PyJobTaskLockedError`
           Locked task, cannot restart or rerun

        """
        if self.locked:
            raise PyJobTaskLockedError('This task is locked!')
        self.script_container.dump()
        self._run()
        logger.debug('Started execution of %s [%d]', self.__class__.__name__, self.pid)
        self.locked = True

    def wait(self, check_success=None, interval=30, monitor=None):
        """Method to wait for the completion of the current :obj:`~pyjob.task.Task`

        Parameters
        ----------
        check_success : func, optional
           A :obj:`callable` to check the success status of a :obj:`~pyjob.task.Task`
        interval : int, optional
           The interval to wait between checking (in seconds)
        monitor : func, optional
           A :obj:`callable` that is regularly invoked

        Note
        ----
        The `check_success` argument needs to accept a log file as input and return
        a :obj:`bool`.

        """
        do_check_success = bool(check_success and callable(check_success))
        if do_check_success:
            msg = 'Checking for %s %d success with function %s'
            logger.debug(msg, self.__class__.__name__, self.pid, check_success.__name__)
        do_monitor = bool(monitor and callable(monitor))
        while not self.completed:
            if do_check_success:
                for log in self.log:
                    if os.path.isfile(log) and check_success(log):
                        logger.debug("%s %d succeeded, run log: %s", self.__class__.__name__, self.pid, log)
                        self.kill()
            if do_monitor:
                monitor()
            time.sleep(interval)


class ClusterTask(Task):
    """Abstract base class for executable cluster tasks"""

    def __init__(self, *args, **kwargs):
        """Instantiate a new :obj:`~pyjob.task.ClusterTask`"""
        super(ClusterTask, self).__init__(*args, **kwargs)
        self.dependency = kwargs.get('dependency', [])
        self.max_array_size = kwargs.get('max_array_size', len(self.script))
        self.priority = kwargs.get('priority', None)
        self.queue = kwargs.get('queue', None)
        self.runtime = kwargs.get('runtime', None)
        self.shell = kwargs.get('shell', None)
        self.name = kwargs.get('name', 'pyjob')
        self.extra = kwargs.get('extra', [])

    @abc.abstractmethod
    def _create_runscript(self):
        """Utility method to create a :obj:`~pyjob.task.ClusterTask` runscript"""
        pass
