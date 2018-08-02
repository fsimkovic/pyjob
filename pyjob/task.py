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
from pyjob.script import is_valid_script_path

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
        
        Raises
        ------
        :exc:`PyJobError`
           One or more scripts cannot be found or are not executable

        """
        self.pid = None
        self.locked = False

        if isinstance(script, str) and is_valid_script_path(script):
            self.script = [script]
        elif (isinstance(script, list) or isinstance(script, tuple)) and all(
                is_valid_script_path(fpath) for fpath in script):
            self.script = list(script)
        else:
            raise PyJobError('One or more scripts cannot be found or are not executable')

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
        self.close()

    def __repr__(self):
        """Representation of the :obj:`~pyjob.task.Task`"""
        return '{}(pid={})'.format(self.__class__.__name__, self.pid)

    # ------------------ Abstract methods and properties ------------------

    @abc.abstractproperty
    def info(self):
        """Abstract property to provide info about the :obj:`~pyjob.task.Task`"""
        pass

    @abc.abstractmethod
    def close(self):
        """Abstract method to end :obj:`~pyjob.task.Task`"""
        pass

    @abc.abstractmethod
    def kill(self):
        """Abstract method to forcefully terminate :obj:`~pyjob.task.Task`"""
        pass

    @abc.abstractmethod
    def _run(self):
        """Abstract property to start execution of the :obj:`~pyjob.task.Task`"""
        pass

    # ------------------ Other task-specific general methods ------------------

    @property
    def completed(self):
        """Boolean to indicate :obj:`~pyjob.task.Task` completion"""
        return not bool(self.info)

    @property
    def log(self):
        """The log file path"""
        return [script.rsplit('.', 1)[0] + '.log' for script in self.script]

    def add_script(self, script):
        """Add further scripts to this :obj:`~pyjob.task.Task`
        
        Parameters
        ----------
        script : str
           A :obj:`str` of script path

        Raises
        ------
        :exc:`~pyjob.exception.PyJobError`
           Script cannot be found or is not executable

        """
        if is_valid_script_path(script):
            self.script.append(script)
        else:
            raise PyJobError('Script cannot be found or is not executable')

    def run(self):
        """Start the execution of this :obj:`~pyjob.sge.SunGridEngineTask`
        
        Raises
        ------
        :exc:`~pyjob.exception.PyJobTaskLockedError`
           Locked task, cannot restart or rerun

        """
        if self.locked:
            raise PyJobTaskLockedError('This task is locked!')
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
