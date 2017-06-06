# MIT License
#
# Copyright (c) 2017 Felix Simkovic
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

"""Module for script containers"""

__author__ = "Felix Simkovic"
__date__ = "05 Jun 2017"
__version__ = "0.1"

import os


# Store what scripts we currently offer
SCRIPT_FORMATS = [
    ("bash", ".sh", "#!/bin/bash"),
    ("batch", ".bat", None),
    ("perl", ".pl", "#!/usr/bin/env perl"),
    ("python", ".py", "#!/usr/bin/env python"),
    ("shell", ".sh", "#!/bin/sh"),
    ("rscript", ".R", "#!/usr/bin/env Rscript"),
]


class _ScriptFormat(object):
    """Class to store all script associated info"""
    __slots__ = ["extension", "handle", "shebang"]

    def __init__(self, extension, handle, shebang):
        """Instantiate a new :obj:`ScriptFormat`"""
        self.extension = extension
        self.handle = handle
        self.shebang = shebang

    def __repr__(self):
        return "{0}(handle=\"{1}\", ext=\"{2}\", shebang=\"{3}\")".format(
            self.__class__.__name__, self.handle, self.extension, self.shebang
        )


class _ScriptFormatter(object):
    """Simple storage class for script formats"""

    def __init__(self):
        """Instantiate a new :obj:`ScriptFormatter`"""
        self._format_dict = {}
        self._format_list = []

        # Initialise with known formats
        for handle, extension, shebang in SCRIPT_FORMATS:
            self.add(extension, handle, shebang)

    def __getitem__(self, item):
        """Return a :obj:`ScriptFormat` entry"""
        return self._format_dict[item]

    def __repr__(self):
        return "{0}(formats=[ {1} ])".format(
            self.__class__.__name__, " | ".join(self._format_dict.keys())
        )

    def add(self, extension, handle, shebang):
        """Add a new entry to the formatter"""
        if handle in self._format_dict:
            raise ValueError("Handle unavailable: {0}!".format(handle))

        sf = _ScriptFormat(extension, handle, shebang)
        self._format_dict[handle] = sf
        self._format_list += [sf]

# Instantiate only single time
ScriptFormatter = _ScriptFormatter()


class _ScriptLine(object):
    """Line container"""
    def __init__(self, entry):
        if isinstance(entry, list) or isinstance(entry, tuple):
            self.entry = " ".join(map(str, entry))
        elif isinstance(entry, str):
            self.entry = entry.strip(os.linesep)
        else:
            raise ValueError("Cannot store line - {0}".format(entry))


class _ScriptContent(object):
    """Content container for scripts"""
    def __init__(self):
        self._lines = []

    def __add__(self, cmd):
        if isinstance(cmd, list) and isinstance(cmd[0], list):
            for c in cmd:
                self._lines += [_ScriptLine(c)]
        elif isinstance(cmd, tuple) and isinstance(cmd[0], tuple):
            for c in cmd:
                self._lines += [_ScriptLine(c)]
        else:
            self._lines += [_ScriptLine(cmd)]

    def __iter__(self):
        """Iterator"""
        for l in self._lines:
            yield l


class Script(object):
    """Script class"""

    def __init__(self, handle):
        """Instantiate a new :obj:`Script` class"""
        self._script_content = _ScriptContent()
        self._formatter = ScriptFormatter[handle]

    @property
    def content(self):
        """The content of the script"""
        content_str = os.linesep.join([
            sc.entry for sc in self._script_content
        ])
        return content_str

    @property
    def formatted(self):
        """The full script formatted with header"""
        content_str = self._formatter.shebang + os.linesep
        content_str += os.linesep.join([
            sc.entry for sc in self._script_content
        ])
        return content_str

    def add(self, cmd):
        """Add some content to the script"""
        self._script_content + cmd
