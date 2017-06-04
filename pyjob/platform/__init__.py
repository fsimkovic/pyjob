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


# Little factory function to get the right platform without importing all
def platform_factory(qtype):
    """Return the correct platform handler"""
    qtype = qtype.lower()
    if qtype == "local":
        from pyjob.platform.local import LocalJobServer
        return LocalJobServer
    elif qtype == "lsf":
        from pyjob.platform.lsf import LoadSharingFacility
        return LoadSharingFacility
    elif qtype == "sge":
        from pyjob.platform.sge import SunGridEngine
        return SunGridEngine
    else:
        raise ValueError("Unknown platform")

