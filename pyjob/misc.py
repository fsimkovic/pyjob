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

import chardet.universaldetector
import os
import sys
import tempfile

from pyjob.deprecate import deprecate
from pyjob.exception import PyJobError


@deprecate(0.3, msg='use pyjob.stopwatch.StopWatch')
def StopWatch():
    from pyjob.stopwatch import StopWatch
    return StopWatch()


def decode(s):
    """Decode a string by guessing the encoding

    Parameters
    ----------
    s : str
       The :obj:`str` to decode

    Returns
    -------
    :obj:`str`
       `s` decoded

    Raises
    ------
    :exc:`PyJobError`
       Unable to infer string encoding
    
    """
    detector = chardet.universaldetector.UniversalDetector()
    for line in s.split(os.linesep):
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    if detector.result['confidence'] < 0.98:
        raise PyJobError('Unable to infer string encoding')
    return s.decode(detector.result['encoding'])


@deprecate(0.3, msg='use pyjob.stopwatch.StopWatch')
def is_script(f):
    from pyjob.script import is_valid_script_path
    return is_valid_script_path(f)


@deprecate(0.3, msg='use pyjob.script.Script')
def make_script(cmd, **kwargs):
    from pyjob.script import Script
    script = Script(**kwargs)
    if isinstance(cmd, list) and isinstance(cmd[0], list) \
            or isinstance(cmd, tuple) and isinstance(cmd[0], tuple) \
            or isinstance(cmd, list) and isinstance(cmd[0], tuple) \
            or isinstance(cmd, tuple) and isinstance(cmd[0], list):
        for c in cmd:
            script.append(' '.join(map(str, c)))
    elif isinstance(cmd, list) or isinstance(cmd, tuple):
        script.append(' '.join(map(str, cmd)))
    script.write()
    return script.path


@deprecate(0.3, msg='use pyjob.script.Script')
def make_python_script(cmd, directory=None, prefix="tmp", stem=None):
    return make_script(
        cmd,
        directory=directory,
        shebang="#!/usr/bin/env python",
        prefix=prefix,
        stem=stem,
        suffix=".py")


@deprecate(0.3)
def tmp_dir(directory=None, prefix="tmp", suffix=""):
    """Return a filename for a temporary directory 

    Parameters
    ----------
    directory : str, optional
       Path to a directory to write the files to.
    prefix : str, optional
       A prefix to the temporary filename
    suffix : str, optional
       A suffix to the temporary filename

    """
    return tempfile.mkdtemp(dir=directory, prefix=prefix, suffix=suffix)


@deprecate(0.3)
def tmp_file(delete=False, directory=None, prefix="tmp", stem=None, suffix=""):
    """Return a filename for a temporary file

    The naming convention of scripts will be ``prefix`` + ``stem`` + ``suffix``.

    Parameters
    ----------
    delete : bool, optional
       Delete the file, thus return name only [default: True]
    directory : str, optional
       Path to a directory to write the files to
    prefix : str, optional
       A prefix to the temporary filename
    stem : str, optional
       The steam part of the script name
    suffix : str, optional
       A suffix to the temporary filename

    """
    if directory is None:
        directory = tempfile.gettempdir()
    if stem is None:
        tmpf = tempfile.NamedTemporaryFile(
            delete=delete, dir=directory, prefix=prefix, suffix=suffix)
        tmpf.close()
        return tmpf.name
    else:
        tmpf = os.path.join(directory, "".join([prefix, stem, suffix]))
        if not delete:
            open(tmpf, 'w').close()
        return tmpf
