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
__contibutors__ = ['Jens Thomas']
__version__ = '1.0'

import logging
import os
import signal
import subprocess
import sys
import warnings

from pyjob.exception import PyJobExecutableNotFoundError, PyJobExecutionError
from pyjob.misc import decode

logger = logging.getLogger(__name__)


def _insert_or_ignore(d, k, v):
    if k not in d:
        d[k] = v


def is_exe(fpath):
    """Status to indicate if a file is an executable

    Parameters
    ----------
    fpath : str
       The path to the file to be tested

    Returns
    -------
    bool

    """
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(executable):
    """Python-based mirror of UNIX ``which`` command

    Parameters
    ----------
    executable : str
       The path or name for an executable

    Returns
    -------
    str
       The absolute path to the executable, or ``None`` if not found

    Credits
    -------
    https://stackoverflow.com/a/377028/3046533

    """
    fpath, fname = os.path.split(executable)
    if fpath:
        if is_exe(executable):
            return executable
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, executable)
            if is_exe(exe_file):
                return exe_file
    return None


def cexec(cmd, permit_nonzero=False, **kwargs):
    """Function to execute a command

    Parameters
    ----------
    cmd : list
       The command to call
    permit_nonzero : bool, optional
       Allow non-zero return codes [default: False]
    **kwargs : dict, option
       Any keyword arguments accepted by :obj:`~subprocess.Popen`

    Returns
    -------
    str
       The processes' standard out

    Raises
    ------
    :exc:`PyJobExecutableNotFoundError`
       Cannot find executable
    :exc:`PyJobExecutionError`
       Execution exited with non-zero return code

    """
    logger.debug("Executing '%s'", " ".join(cmd))

    if os.name == 'nt':
        _insert_or_ignore(kwargs, 'bufsize', 0)
        _insert_or_ignore(kwargs, 'shell', 'False')
    if 'directory' in kwargs:
        warnings.warn('directory keywoard has been deprecated, use cwd instead', DeprecationWarning)
        kwargs['cwd'] = kwargs['directory']
        kwargs.pop('directory')
    _insert_or_ignore(kwargs, 'cwd', os.getcwd())
    _insert_or_ignore(kwargs, 'stdout', subprocess.PIPE)
    _insert_or_ignore(kwargs, 'stderr', subprocess.STDOUT)

    stdinstr = kwargs.get('stdin', None)
    if stdinstr and isinstance(stdinstr, str):
        kwargs['stdin'] = subprocess.PIPE

    executable = which(cmd[0])
    if executable is None:
        warnings.warn('executable not in PATH. provide absolute path to executable in future', DeprecationWarning)
    #      raise PyJobExecutableNotFoundError('Cannot find executable: %s' % cmd[0])
    #  cmd[0] = executable

    try:
        p = subprocess.Popen(cmd, **kwargs)
        if stdinstr:
            stdinstr = stdinstr.encode()
        stdout, stderr = p.communicate(input=stdinstr)
    except (KeyboardInterrupt, SystemExit):
        os.kill(p.pid, signal.SIGTERM)
        sys.exit(signal.SIGTERM)
    else:
        if stdout:
            stdout = decode(stdout).strip()
        if p.returncode == 0:
            return stdout
        elif permit_nonzero:
            logger.debug("Ignoring non-zero returncode %d for '%s'", p.returncode, " ".join(cmd))
            return stdout
        else:
            msg = "Execution of '{}' exited with non-zero return code ({})"
            raise PyJobExecutionError(msg.format(' '.join(cmd), p.returncode))
