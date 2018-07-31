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
__date__ = '29 Jul 2018'
__version__ = '1.0'

from contextlib import contextmanager
from multiprocessing import Pool


@contextmanager
def Pool(*args, **kwargs):
    """:obj:`~multiprocessing.pool.Pool` of processes to allow concurrent method calls
    
    This function creates a context for normal :obj:`~multiprocessing.pool.Pool` 
    instances. This allows controlled termination for :exc:`RuntimeError` 
    and :exc:`KeyboardInterrupt` exceptions.

    Examples
    --------

    >>> from pyjob import Pool
    >>> with Pool(processes=4) as pool:
    ...     pool.map(callable, [iterable])

    Parameters
    ----------
    *args : tuple
       Positional arguments for :obj:`~multiprocessing.pool.Pool`
    **kwargs : dict
       Keyword arguments for :obj:`~multiprocessing.pool.Pool`

    Yields
    ------
    :obj:`~multiprocessing.pool.Pool`
       An instance to a :obj:`~multiprocessing.pool.Pool`

    """
    pool = Pool(*args, **kwargs)
    try:
        yield pool
    except (RuntimeError, KeyboardInterrupt) as e:
        pool.terminate()
        raise e
    else:
        pool.close()
