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

from pyjob.factory import TaskFactory
from pyjob.misc import deprecate


class Job(object):
    @deprecate(0.3, msg='Use Task/TaskFactory instead')
    def __init__(self, qtype):
        self.qtype = qtype
        self._task = None
        self._locked = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._task:
            self._task.close()

    def __del__(self):
        if self._task:
            self._task.close()

    @property
    def finished(self):
        return self._task.completed

    @property
    def pid(self):
        return self._task.pid

    @property
    def log(self):
        return self._task.log

    @property
    def script(self):
        return self._task.script

    def kill(self):
        self._task.kill()

    def submit(self, script, *args, **kwargs):
        if self._locked:
            return
        kwargs['processes'] = kwargs.get('nproc', None)
        self._task = TaskFactory(self.qtype, script, *args, **kwargs)
        self._task.run()
        self._locked = True

    def stat(self):
        return self._task.info

    def wait(self, *args, **kwargs):
        self._task.wait(*args, **kwargs)
