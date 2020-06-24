import logging
import os
import signal
import subprocess
import sys

from pyjob.exception import PyJobExecutableNotFoundError, PyJobExecutionError
from pyjob.misc import decode

logger = logging.getLogger(__name__)


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
    executable = which(cmd[0])
    if executable is None:
        raise PyJobExecutableNotFoundError(f"Cannot find executable: {cmd[0]}")
    cmd[0] = executable

    logger.debug('Executing "%s"', " ".join(cmd))

    if os.name == "nt":
        kwargs.setdefault("bufsize", 0)
        kwargs.setdefault("shell", "False")

    kwargs.setdefault("cwd", os.getcwd())
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("stderr", subprocess.STDOUT)

    stdinstr = kwargs.get("stdin", None)
    if stdinstr and isinstance(stdinstr, str):
        kwargs["stdin"] = subprocess.PIPE

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
            logger.debug(
                "Ignoring non-zero returncode %d for '%s'", p.returncode, " ".join(cmd)
            )
            return stdout
        else:
            raise PyJobExecutionError(
                f"Execution of '{' '.join(cmd)}' exited with non-zero return code ({p.returncode})"
            )
