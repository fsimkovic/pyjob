"""Available platforms"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"
__version__ = "0.1"

import sys

# OS-dependent script headers and extensions
if sys.platform.startswith('win'):
    EXE_EXT, SCRIPT_HEADER, SCRIPT_EXT = ('.exe', '', '.bat')
else:
    EXE_EXT, SCRIPT_HEADER, SCRIPT_EXT = ('', '#!/bin/bash', '.sh')


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

