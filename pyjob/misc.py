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
import warnings

from pyjob.exception import PyJobError


def decode(byte_s):
    """Decode a string by guessing the encoding

    Parameters
    ----------
    byte_s : bytes
       The :obj:`bytes` to decode

    Returns
    -------
    :obj:`str`
       `byte_s` decoded

    Raises
    ------
    :exc:`PyJobError`
       Unable to infer string encoding

    """
    detector = chardet.universaldetector.UniversalDetector()
    for line in byte_s.splitlines():
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    if detector.result['confidence'] < 0.98:
        raise PyJobError('Unable to infer string encoding')
    return byte_s.decode(detector.result['encoding'])


def deprecate(version, msg=None):
    """Decorator to deprecate Python classes and functions

    Parameters
    ----------
    version : str
       A string containing the version with which the callable is removed
    msg : str, optional
       An additional message that will be displayed alongside the default message


    Examples
    --------
    Enable :obj:`~DeprecationWarning` messages to be displayed.

    >>> import warnings
    >>> warnings.simplefilter('default')

    Decorate a simple Python function without additional message

    >>> @deprecate('0.0.0')
    ... def sum(a, b):
    ...     return a + b
    >>> sum(1, 2)
    deprecated.py:34: DeprecationWarning: sum has been deprecated and will be removed in version 0.0.0!
      warnings.warn(message, DeprecationWarning)
    3

    Decorate a simple Python function with additional message

    >>> @deprecate('0.0.1', msg='Use XXX instead!')
    ... def sum(a, b):
    ...     return a + b
    >>> sum(2, 2)
    deprecated.py:34: DeprecationWarning: sum has been deprecated and will be removed in version 0.0.0!
      warnings.warn(message, DeprecationWarning)
    4

    Decorate an entire Python class

    >>> @deprecate('0.0.2')
    ... class Obj(object):
    ...     pass
    >>> Obj()
    deprecated.py:34: DeprecationWarning: Obj has been deprecated and will be removed in version 0.0.2!
      warnings.warn(message, DeprecationWarning)
    <__main__.Obj object at 0x7f8ee0f1ead0>

    Decorate a Python class method

    >>> class Obj(object):
    ...     def __init__(self, v):
    ...         self.v = v
    ...     @deprecate('0.0.3')
    ...     def mul(self, other):
    ...         return self.v * other.v
    >>> Obj(2).mul(Obj(3))
    deprecated.py:34: DeprecationWarning: mul has been deprecated and will be removed in version 0.0.3!
      warnings.warn(message, DeprecationWarning)
    6

    Decorate a Python class staticmethod

    >>> class Obj(object):
    ...     @staticmethod
    ...     @deprecate('0.0.4')
    ...     def sub(a, b):
    ...         return a - b
    ...
    >>> Obj.sub(2, 1)
    deprecated.py:34: DeprecationWarning: sub has been deprecated and will be removed in version 0.0.4!
      warnings.warn(message, DeprecationWarning)
    1

    Decorate a Python class classmethod

    >>> class Obj(object):
    ...     CONST = 5
    ...     @classmethod
    ...     @deprecate('0.0.5')
    ...     def sub(cls, a):
    ...         return a - cls.CONST
    ...
    >>> Obj().sub(5)
    deprecated.py:34: DeprecationWarning: sub has been deprecated and will be removed in version 0.0.5!
      warnings.warn(message, DeprecationWarning)
    0

    """

    def deprecate_decorator(callable_):
        def warn(*args, **kwargs):
            message = "%s has been deprecated and will be removed in version %s!" % (callable_.__name__, version)
            if msg:
                message += " - %s" % msg
            warnings.warn(message, DeprecationWarning)
            return callable_(*args, **kwargs)

        return warn

    return deprecate_decorator


def typecast(value):
    """Recursively typecast an input

    Parameters
    ----------
    value : int, float, str, tuple, list

    """
    if isinstance(value, (list, tuple)):
        for i in range(len(value)):
            value[i] = typecast(v)
    elif value == 'None':
        return None
    else:
        for c in [int, float, str]:
            try:
                return c(value)
            except ValueError:
                pass


@deprecate(0.3, msg='use pyjob.stopwatch.StopWatch')
def is_script(f):
    from pyjob.script import is_valid_script_path
    return is_valid_script_path(f)


@deprecate(0.3, msg='use pyjob.stopwatch.StopWatch')
def StopWatch():
    from pyjob.stopwatch import StopWatch
    return StopWatch()


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
    elif isinstance(cmd, (list, tuple)):
        script.append(' '.join(map(str, cmd)))
    script.write()
    return script.path


@deprecate(0.3, msg='use pyjob.script.Script')
def make_python_script(cmd, directory=None, prefix="tmp", stem=None):
    return make_script(
        cmd, directory=directory, shebang="#!/usr/bin/env python", prefix=prefix, stem=stem, suffix=".py")


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
        tmpf = tempfile.NamedTemporaryFile(delete=delete, dir=directory, prefix=prefix, suffix=suffix)
        tmpf.close()
        return tmpf.name
    else:
        tmpf = os.path.join(directory, "".join([prefix, stem, suffix]))
        if not delete:
            open(tmpf, 'w').close()
        return tmpf
