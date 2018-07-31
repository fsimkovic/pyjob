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

import logging
import os
import signal
import subprocess
import sys

from pyjob.exception import PyJobExecutionError

logger = logging.getLogger(__name__)


def cexec(cmd, directory=None, stdin=None, permit_nonzero=False):
    """Function to execute a command

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
    PyJobExecutionError
       Execution exited with non-zero return code

    """
    logger.debug("Executing '%s'", " ".join(cmd))
    kwargs = {"bufsize": 0, "shell": "False"} if os.name == "nt" else {}
    kwargs['cwd'] = directory
    kwargs['stdin'] = subprocess.PIPE
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.STDOUT
    try:
        p = subprocess.Popen(cmd, **kwargs)
        if stdin:
            stdin = stdin.encode()
        stdout, _ = p.communicate(input=stdin)
    except KeyboardInterrupt:
        os.kill(p.pid, signal.SIGTERM)
        sys.exit(signal.SIGTERM)
    else:
        stdout = stdout.decode()
        if p.returncode == 0:
            return stdout.strip()
        elif permit_nonzero:
            logger.debug("Ignoring non-zero returncode %d for '%s'",
                         p.returncode, " ".join(cmd))
            return stdout.strip()
        else:
            msg = "Execution of '{}' exited with non-zero return code ({})"
            raise PyJobExecutionError(msg.format(' '.join(cmd), p.returncode))
