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
    if isinstance(value, (dict, list)):
        iterator = range(len(value)) if isinstance(value, list) else value
        for i in iterator:
            value[i] = typecast(value[i])
    elif value == 'None':
        return None
    elif value in ('False', 'True'):
        return True if value == 'True' else False
    else:
        for type_fn in (int, float, str):
            try:
                return type_fn(value)
            except ValueError:
                pass
    return value
