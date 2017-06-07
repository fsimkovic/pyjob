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

"""Container for the most basic platform layout"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"
__version__ = "0.1"

from pyjob.exception import PyJobNotImplemented


class _Platform(object):
    """Container for job management platforms. 
    
    Notes
    -----
    Do not instantiate directly but use child classes instead.
    
    """

    TASK_ID = None

    @staticmethod
    def alt(*args, **kwargs):
        raise PyJobNotImplemented("Function unavailable for specified queue type")

    @staticmethod
    def hold(*args, **kwargs):
        raise PyJobNotImplemented("Function unavailable for specified queue type")

    @staticmethod
    def kill(*args, **kwargs):
        raise PyJobNotImplemented("Function unavailable for specified queue type")

    @staticmethod
    def rls(*args, **kwargs):
        raise PyJobNotImplemented("Function unavailable for specified queue type")

    @staticmethod
    def sub(*args, **kwargs):
        raise PyJobNotImplemented("Function unavailable for specified queue type")

    @staticmethod
    def stat(*args, **kwargs):
        raise PyJobNotImplemented("Function unavailable for specified queue type")


class ClusterPlatform(_Platform):
    """Container for cluster platforms"""
    pass


class LocalPlatform(_Platform):
    """Container for local platforms"""
    pass
