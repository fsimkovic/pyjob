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

from pyjob.exception import PyJobUnknownFormat

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
    __slots__ = ["extension", "format", "shebang"]

    def __init__(self, extension, format, shebang):
        """Instantiate a new :obj:`ScriptFormat`"""
        self.extension = extension
        self.format = format
        self.shebang = shebang

    def __repr__(self):
        return "{0}(format=\"{1}\", ext=\"{2}\", shebang=\"{3}\")".format(
            self.__class__.__name__, self.format, self.extension, self.shebang
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

    def __iter__(self):
        """Iterator over formatter"""
        for sformat in self._format_list:
            yield sformat

    def __repr__(self):
        return "{0}(formats=[ {1} ])".format(
            self.__class__.__name__, " | ".join(self._format_dict.keys())
        )

    @property
    def extensions(self):
        """All available file extensions"""
        return [f.extension for f in self]

    @property
    def formats(self):
        """All available file formats"""
        return [f.format for f in self]

    @property
    def shebangs(self):
        """All available file shebangs"""
        return [f.shebang for f in self]

    def add(self, extension, handle, shebang):
        """Add a new entry to the formatter"""
        if handle in self._format_dict:
            raise ValueError("Handle unavailable: {0}!".format(handle))

        sf = _ScriptFormat(extension, handle, shebang)
        self._format_dict[handle] = sf
        self._format_list += [sf]

# Instantiate only single time
ScriptFormatter = _ScriptFormatter()


class Script(object):
    """Script class"""

    def __init__(self, format, content=None):
        """Instantiate a new :obj:`Script` class"""
        self._script_content = content
        self._formatter = ScriptFormatter[format]

    def __repr__(self):
        pass

    @property
    def content(self):
        """The content of the script"""
        return self._script_content

    @content.setter
    def content(self, content):
        """Define the content of the script"""
        self._script_content = content

    @property
    def formatted(self):
        """The full script formatted with header"""
        content_str = os.linesep.join([
            self._formatter.shebang,
            self._script_content,
        ])
        return content_str

    def to_file(self, fname):
        """Write the script content to a file
        
        Parameters
        ----------
        fname : str
           The filename of the script
        
        Returns
        -------
        str
           The absolute path to the script name
        
        Notes
        -----
        If no/incorrect extension, the correct will be appended!
        
        """
        if not fname.endswith(self._formatter.extension):
            fname += self._formatter.extension
        with open(fname, "w") as f_out:
            f_out.write(self.formatted)
        os.chmod(fname, 0o777)
        return os.path.abspath(fname)


def read_file(fname, format=None):
    """Read a script from a filename

    The format of the script will be attempted to be established by
        1. The shebang line
        2. The script extension

    Parameters
    ----------
    fname : str
       The filename of the script
    format : str, optional
       The script format

    Returns
    -------
    obj
       A :obj:`Script <pyjob.script.Script>` instance

    """
    # Read the script
    with open(fname, "r") as f_in:
        fcontent = f_in.read()
    lines = fcontent.split(os.linesep)

    # Find format by shebang
    if format is None and lines[0].startswith("#!"):
        shebang = lines[0]
        # Shebang looks like "#!/usr/bin/python"
        if len(shebang.split()) == 1:
            format = shebang.split(os.sep)[-1]
            lines.pop(0)
        # Shebang looks like "#!/usr/bin/env python"
        elif len(shebang.split()) == 2:
            format = shebang.split()[1]
            lines.pop(0)
    elif lines[0].startswith("#!"):
        lines.pop(0)

    # Attempt by file extension
    if format is None:
        # Attempt to guess it by the script extension
        for ext, form in zip(ScriptFormatter.extensions, ScriptFormatter.formats):
            if fname.endswith(ext):
                format = form
                break

    # Nothing found
    if format is None:
        raise PyJobUnknownFormat("Cannot identify format, please specify")

    # Get the content
    content = os.linesep.join(lines).strip()

    return Script(format, content=content)