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
__contributors__ = ['Adam Simpkin']
__version__ = '1.0'

import enum
import os
import sys

from pyjob.cexec import is_exe
from pyjob.exception import PyJobError
from pyjob.pool import Pool


@enum.unique
class ScriptProperty(enum.Enum):
    """Enumeration for :obj:`~pyjob.script.Script`-specific properties"""
    # Tried to extend Enum but operation not allowed in Python3.7
    # https://docs.python.org/3/library/enum.html#restricted-subclassing-of-enumerations
    if sys.platform.startswith('win'):
        PERL = ('', '.pl')
        PYTHON = ('', '.py')
        SHELL = ('', '.bat')
    else:
        PERL = ('#!/usr/bin/env perl', '.pl')
        PYTHON = ('#!/usr/bin/env python', '.py')
        SHELL = ('#!/bin/bash', '.sh')

    def __init__(self, shebang, suffix):
        self.shebang = shebang
        self.suffix = suffix


if sys.platform.startswith('win'):
    EXE_EXT = '.exe'
else:
    EXE_EXT = ''

SCRIPT_HEADER, SCRIPT_EXT = (ScriptProperty.SHELL.shebang, ScriptProperty.SHELL.suffix)


class ScriptCollector(object):
    """A :obj:`~pyjob.script.ScriptCollector` to store executable :obj:`~pyjob.script.Script` instances

    Examples
    --------

    >>> from pyjob.script import ScriptCollector, Script
    >>> collector = ScriptCollector(None)
    >>> for _ in range(5):
    ...     collector.add(Script())

    """

    def __init__(self, scripts):
        """Instantiate a new :obj:`~pyjob.script.ScriptCollector`"""
        self._container = []
        self._save_script(scripts)

    def __iter__(self):
        """Iterator function"""
        for script in self._container:
            yield script

    def __len__(self):
        """Length function"""
        return len(self._container)

    def __repr__(self):
        """Representation function"""
        return '{}(nscripts={})'.format(self.__class__.__name__, len(self))

    @property
    def scripts(self):
        """The script file paths"""
        return self._container

    @scripts.setter
    def scripts(self, scripts):
        """The script file paths

        Parameters
        ----------
        script : :obj:`~pyjob.script.Script`, str, list, tuple
           Something representing one or more scripts

        Raises
        ------
        :exc:`~pyjob.exception.PyJobError`
           Script cannot be found or is not executable

        """
        self._container = []
        self._save_script(scripts)

    def add(self, scripts):
        """Add one or more script file paths

        Parameters
        ----------
        script : :obj:`~pyjob.script.Script`, str, list, tuple
           Something representing one or more scripts

        Raises
        ------
        :exc:`~pyjob.exception.PyJobError`
           Script cannot be found or is not executable

        """
        self._save_script(scripts)

    def dump(self):
        """Write all scripts to disk if not already done"""
        for script in self._container:
            if not os.path.isfile(script.path):
                script.write()

    def _save_script(self, script):
        """Helper function to assess/standardise executable input

        Parameters
        ----------
        script : :obj:`~pyjob.executable.Script`, str, list, tuple
           Something representing one or more executables

        Raises
        ------
        :exc:`~pyjob.exception.PyJobError`
           Unrecognised executable input

        """
        if isinstance(script, Script):
            self._container.append(script)
        elif isinstance(script, str):
            script = Script.read(script)
            self._container.append(script)
        elif isinstance(script, (list, tuple)):
            for s in script:
                if isinstance(s, Script):
                    self._container.append(s)
                elif isinstance(s, str):
                    self._container.append(Script.read(s))
                else:
                    raise PyJobError('Unrecognised executable input')
        elif script is None:
            pass
        else:
            raise PyJobError('Unrecognised executable input')


class Script(list):
    """Simple extension to :obj:`list` to hold the contents for an executable script

    Examples
    --------

    >>> from pyjob import Script
    >>> script = Script(directory='.', prefix='example', stem='', suffix='.sh')
    >>> script.append('sleep 5')
    >>> print(script)
    #!/bin/bash
    sleep 5

    """

    def __init__(self,
                 shebang=ScriptProperty.SHELL.shebang,
                 directory='.',
                 prefix='tmp',
                 stem='pyjob',
                 suffix=ScriptProperty.SHELL.suffix):
        """Instantiate a new :obj:`~pyjob.script.Script`

        Parameters
        ----------
        shebang : str, optional
           The Shebang line in the :obj:`~pyjob.script.Script`
        directory : str, optional
           The directory for :obj:`~pyjob.script.Script` storage
        prefix : str, optional
           The :obj:`~pyjob.script.Script` filename prefix
        stem : str, optional
           The :obj:`~pyjob.script.Script` filename middle
        suffix : str, optional
           The :obj:`~pyjob.script.Script` filename suffix

        """
        self.directory = directory
        self.prefix = prefix
        self.stem = stem
        self.suffix = suffix
        self.shebang = shebang

    def __add__(self, other):
        """Combine two :obj:`~pyjob.script.Script` instances"""
        if self.shebang != other.shebang:
            raise TypeError('Invalid shebang combination')
        if self.suffix != other.suffix:
            raise TypeError('Invalid suffix combination')
        script = Script(stem=self.stem + '-' + other.stem, shebang=self.shebang, suffix=self.suffix)
        script.content = [line for script in [self, other] for line in script]
        return script

    def __str__(self):
        """Content of :obj:`~pyjob.script.Script`"""
        content = self[:]
        if len(self.shebang) > 0:
            content.insert(0, self.shebang)
        return '\n'.join(map(str, content))

    @property
    def content(self):
        """Getter method for :attr:`~pyjob.script.Script` content"""
        return self

    @content.setter
    def content(self, content):
        """Setter method for :attr:`~pyjob.script.Script` content"""
        while len(self) > 0:
            self.pop()
        self.extend(content)

    @property
    def directory(self):
        """Getter method for :attr:`~pyjob.script.Script.directory`"""
        return self._directory

    @directory.setter
    def directory(self, directory):
        """Setter method for :attr:`~pyjob.script.Script.directory`"""
        self._directory = os.path.abspath(directory)

    @property
    def log(self):
        """Path to the log of the the :obj:`~pyjob.script.Script`"""
        return self.path.rsplit('.', 1)[0] + '.log'

    @property
    def path(self):
        """Path to the :obj:`~pyjob.script.Script`"""
        return os.path.join(self.directory, self.prefix + self.stem + self.suffix)

    @property
    def shebang(self):
        """:obj:`~pyjob.script.Script` shebang"""
        return self._shebang

    @shebang.setter
    def shebang(self, value):
        """:obj:`~pyjob.script.Script` shebang"""
        self._shebang = value

    @property
    def suffix(self):
        """:obj:`~pyjob.script.Script` file suffix"""
        return self._suffix

    @suffix.setter
    def suffix(self, value):
        """:obj:`~pyjob.script.Script` file suffix"""
        if value is None or len(value) < 1 or '.' not in value:
            raise ValueError('Script suffix required!')
        self._suffix = value

    def write(self):
        """Write the :obj:`~pyjob.script.Script` to :attr:`~pyjob.script.Script.path`"""
        fname = self.path
        with open(fname, 'w') as f_out:
            f_out.write(str(self))
        os.chmod(fname, 0o777)

    @staticmethod
    def read(path):
        """Read a script file to construct a :obj:`~pyjob.script.Script`

        Examples
        --------

        >>> from pyjob import read_script
        >>> script = read_script('./example.sh')
        >>> print(script)
        #!/bin/bash
        sleep 5

        Parameters
        ----------
        path : str
           The path to a script file

        Returns
        -------
        :obj:`~pyjob.script.Script`
           A :obj:`~pyjob.script.Script` instance

        """
        directory, fname = os.path.split(path)
        fname, ext = os.path.splitext(fname)
        script = Script(directory=directory, prefix='', stem=fname, suffix=ext)
        with open(path, 'r') as f:
            lines = f.read().splitlines()
        if len(lines) > 0 and lines[0][:2] == '#!':
            script.shebang = lines.pop(0)
        else:
            script.shebang = ''
        script.extend(lines)
        return script


class LocalScriptCreator(object):
    """A :obj:`~pyjob.script.ScriptCollector` to store executable :obj:`~pyjob.script.Script`
    instances created in parallel using an input ``func`` to create the scripts.

    Examples
    --------

    >>> from pyjob.script import LocalScriptCreator, Script
    >>> script_creator = LocalScriptCreator(func, iterable, processes)
    >>> collector = script_creator.collector

    """

    def __init__(self, func=None, iterable=None, processes=1):
        """Instantiate a new :obj:`~pyjob.script.LocalScriptCreator`

        Parameters
        ----------
        func : func
            function to create :obj:`~pyjob.script.Script` with custom command
        iterable : iterable
            iterable argument to input into func
        processes : int
            Number of processes to generate scripts with

        """
        self.func = func
        self.iterable = iterable
        self.processes = processes

    def __call__(self, i):
        return self.func(i)

    @property
    def collector(self):
        script_collector = ScriptCollector(None)
        with Pool(processes=self.processes) as pool:
            script_collector.add(pool.map(self, self.iterable))
        return script_collector


def is_valid_script_path(fname):
    """Validate a script path

    Parameters
    ----------
    fname : str
        The path to a script file

    Returns
    -------
    bool

    """
    return is_exe(fname)
