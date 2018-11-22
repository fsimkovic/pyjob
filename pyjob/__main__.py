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
import enum
import logging
import os
import sys

from pyjob import TaskFactory, config, __version__
from pyjob.factory import TASK_PLATFORMS
from pyjob.misc import typecast


class Subcommand(enum.Enum):
    CONF = enum.auto()
    EXEC = enum.auto()
    NONE = enum.auto()


def add_exec_subparser(sp):
    p = sp.add_parser('exec', help='Execute scripts')
    p.add_argument('-d', '--directory', default='.', help='the run directory')
    p.add_argument(
        '-p', '--platform', choices=TASK_PLATFORMS.keys(),
        default=config.get('platform', 'local'), help='the execution platform'
    )
    p.add_argument(
        '-t', '--threads', type=int, dest='processes', default=config.get('processes', 1), help='number of threads'
    )
    p.add_argument('--chdir', action='store_true', default=False, help='execute jobs in script directory')
    p.add_argument(
        '--permit-nonzero', action='store_true', default=False, help='permit non-zero return codes from executables'
    )
    p.add_argument('--verbose', action='count')
    p.add_argument('--version', action='version', version='pyjob ' + __version__)
    p.add_argument('executables', nargs='+', help='one or more executable scripts')
    mark_parser(p, Subcommand.EXEC)


def add_conf_subparser(sp):
    p = sp.add_parser('conf', help='Configuration setup')
    p.add_argument('arguments', nargs='+', help='List of key:value pairs [space-spearated; None key to delete]')
    mark_parser(p, Subcommand.CONF)


def mark_parser(p, label):
    p.set_defaults(which=label)


def main():
    p = argparse.ArgumentParser(prog='pyjob', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    mark_parser(p, Subcommand.NONE)  # may be removed once Py3-only

    sub_p = p.add_subparsers()
    add_exec_subparser(sub_p)
    add_conf_subparser(sub_p)
    args = p.parse_args()

    if args.which == Subcommand.EXEC:
        kwargs = vars(args)
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

    elif args.which == Subcommand.CONF:
        for pair in args.arguments:
            k, v = pair.split(':')
            config.setdefault(k, value=typecast(v))
    else:
        p.print_help()


if __name__ == '__main__':
    main()
