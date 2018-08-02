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

import os
import sys

if sys.platform.startswith('win'):
    EXE_EXT, SCRIPT_HEADER, SCRIPT_EXT = ('.exe', '', '.bat')
else:
    EXE_EXT, SCRIPT_HEADER, SCRIPT_EXT = ('', '#!/bin/bash', '.sh')


class Script(list):
    """Simple extension to :obj:`list` to hold the contents for an executable script"""

    def __init__(self, shebang=SCRIPT_HEADER, directory='.', prefix='tmp', stem='pyjob', suffix=SCRIPT_EXT):
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

    def __str__(self):
        """Content of :obj:`~pyjob.script.Script`"""
        return os.linesep.join([self.shebang] + self)

    @property
    def directory(self):
        """Getter method for :attr:`~pyjob.script.Script.directory`"""
        return self._directory

    @directory.setter
    def directory(self, directory):
        """Setter method for :attr:`~pyjob.script.Script.directory`"""
        self._directory = os.path.abspath(directory)

    @property
    def path(self):
        """Path to the :obj:`~pyjob.script.Script`"""
        return os.path.join(self.directory, self.prefix + self.stem + self.suffix)

    def write(self):
        """Write the :obj:`~pyjob.script.Script` to :attr:`~pyjob.script.Script.path`"""
        fname = self.path
        with open(fname, 'w') as f_out:
            f_out.write(str(self))
        os.chmod(fname, 0o777)

    @staticmethod
    def read(path):
        """Read a script file to construct a :obj:`~pyjob.script.Script`

        Parameters
        ----------
        path : str
           The path to a script file

        Returns
        -------
        :obj:`~pyjob.script.Script`
        
        """
        directory, fname = os.path.split(path)
        fname, ext = os.path.splitext(fname)
        script = Script(directory=directory, prefix='', stem=fname, suffix=ext)
        with open(path, 'r') as f_in:
            lines = [line.rstrip() for line in f_in.readlines()]
        if lines[0][:2] == '#!':
            script.shebang = lines.pop(0)
        script.extend(lines)
        return script


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
    return os.path.isfile(fname) and os.access(fname, os.X_OK)
