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

import argparse
import logging
import os
import sys

from pyjob import TaskFactory, __version__
from pyjob.factory import TASK_PLATFORMS


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-d', '--directory', default='.')
    p.add_argument('-p', '--platform', choices=TASK_PLATFORMS.keys(), default='local')
    p.add_argument('-t', '--threads', default=1, type=int, dest='processes')
    p.add_argument('--chdir', default=False, action='store_true')
    p.add_argument('--permit-nonzero', default=False, action='store_true')
    p.add_argument('--verbose', action='count')
    p.add_argument('--version', action='version', version='pyjob ' + __version__)
    p.add_argument('executables', nargs='+')

    kwargs = vars(p.parse_args())
    platform = kwargs.pop('platform')
    executables = [os.path.abspath(f) for f in kwargs.pop('executables')]
    kwargs['directory'] = os.path.abspath(kwargs['directory'])

    verbosity_lvl = kwargs.pop('verbose')
    if verbosity_lvl == 0:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)

    with TaskFactory(platform, executables, **kwargs) as task:
        task.run()

    sys.exit(0)


if __name__ == '__main__':
    main()
