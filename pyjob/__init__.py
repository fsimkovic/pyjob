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

"""PyJob library for Python-controlled job execution across multiple platforms"""

import logging
import os
import signal
import subprocess
import sys

from pyjob import version
from pyjob.exception import PyJobUnknownFormat

__author__ = "Felix Simkovic"
__email__ = "felixsimkovic@me.com"
__version__ = version.__version__


def Job(*args, **kwargs):
    from pyjob.job import Job
    return Job(*args, **kwargs)


def cexec(cmd, directory=None, stdin=None, permit_nonzero=False):
    """Execute a command

    Parameters
    ----------
    cmd : list
       The command to call
    directory : str, optional
       The directory to execute the job in
    stdin : str, optional
       Additional keywords provided to the command
    permit_nonzero : bool, optional
       Allow non-zero return codes [default: False]

    Returns
    -------
    str
       The processes standard out

    Raises
    ------
    RuntimeError
       Execution exited with non-zero return code

    """
    logger = logging.getLogger(__name__)
    try:
        logger.debug("Executing '%s'", " ".join(cmd))
        kwargs = {"bufsize": 0, "shell": "False"} if os.name == "nt" else {}
        p = subprocess.Popen(cmd, cwd=directory, stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                             stdout=subprocess.PIPE, **kwargs)
        # We require the str.encode() and str.decode() functions for Python 2.x and 3.x compatibility
        stdout, _ = p.communicate(input=stdin.encode()) if stdin else p.communicate()
        stdout = stdout.decode()
        if p.returncode == 0:
            return stdout.strip()
        elif permit_nonzero:
            logger.debug("Ignoring non-zero returncode %d for '%s'", p.returncode, " ".join(cmd))
            return stdout.strip()
        else:
            msg = "Execution of '{0}' exited with non-zero return code ({1}): {2}".format(' '.join(cmd),
                                                                                          p.returncode, stdout)
            raise RuntimeError(msg)
    # Allow ctrl-c's
    except KeyboardInterrupt:
        os.kill(p.pid, signal.SIGTERM)
        sys.exit(signal.SIGTERM)

