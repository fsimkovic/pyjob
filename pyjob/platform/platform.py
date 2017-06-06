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

    TASK_ENV = None

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
