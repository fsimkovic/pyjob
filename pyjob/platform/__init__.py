"""Available platforms"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"
__version__ = "0.1"


def LocalJobServer():
    """Local job management platform"""
    from pyjob.platform.local import LocalJobServer
    return LocalJobServer


def LoadSharingFacility():
    """LoadSharingFacility job management platform"""
    from pyjob.platform.lsf import LoadSharingFacility
    return LoadSharingFacility


def SunGridEngine():
    """SunGridEngine job management platform"""
    from pyjob.platform.sge import SunGridEngine
    return SunGridEngine

