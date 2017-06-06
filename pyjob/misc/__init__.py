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

"""Various functions"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"
__version__ = "0.1"

import os
import tempfile

from pyjob.platform import SCRIPT_EXT, SCRIPT_HEADER


def StopWatch():
    """Import the :obj:`StopWatch <pyjob.misc.stopwatch.StopWatch>`"""
    from pyjob.misc.stopwatch import StopWatch
    return StopWatch()


def is_script(f):
    """Confirm if a script file is executable"""
    return os.path.isfile(f) and os.access(f, os.X_OK)


def make_script(cmd, directory=None, prefix="tmp", stem=None, suffix=SCRIPT_EXT):
    """Create an executable script
    
    Parameters
    ----------
    cmd : list
       The command to be written to the script. This can be a 1-dimensional 
       or 2-dimensional list, depending on the commands to run.
    directory : str, optional
       The directory to create the script in
    prefix : str, optional
       The script prefix [default: None]
    stem : str, optional
       The steam part of the script name
    suffix : str, optional
       The script suffix [default: POSIX - ``.sh``, Windows - ``.bat``]
    
    Returns
    -------
    str
       The path to the script

    """
    # Get the script name
    script = tmp_file(delete=True, directory=directory, prefix=prefix, stem=stem, suffix=suffix)
    # Write the contents to the file
    with open(script, 'w') as f_out:
        content = SCRIPT_HEADER + os.linesep
        if isinstance(cmd, list) and isinstance(cmd[0], list):
            for c in cmd:
                content += ' '.join(map(str, c)) + os.linesep
        elif isinstance(cmd, list):
            content += ' '.join(map(str, cmd)) + os.linesep
        f_out.write(content)
    os.chmod(script, 0o777)
    return script


def make_python_script(cmd, directory=None, prefix="tmp", stem=None, suffix='.py'):
    """Create an executable Python script

    Parameters
    ----------
    cmd : list
       The command to be written to the script. This can be a 1-dimensional 
       or 2-dimensional list, depending on the Python commands to run.
    directory : str, optional
       The directory to create the script in
    prefix : str, optional
       The script prefix [default: None]
    stem : str, optional
       The steam part of the script name
    suffix : str, optional
       The script suffix [default: ``.py``]

    Returns
    -------
    str
       The path to the script

    """
    # Get the script name
    script = tmp_file(delete=True, directory=directory, prefix=prefix, stem=stem, suffix=suffix)
    # Write the contents to the file
    with open(script, 'w') as f_out:
        content = "#!/usr/bin/env python" + os.linesep
        if isinstance(cmd, list) and isinstance(cmd[0], list):
            for c in cmd:
                content += ' '.join(map(str, c)) + os.linesep
        elif isinstance(cmd, list):
            content += ' '.join(map(str, cmd)) + os.linesep
        f_out.write(content)
    os.chmod(script, 0o777)
    return script


def tmp_dir(directory=None, prefix="tmp", suffix=""):
    """Return a filename for a temporary directory 

    Parameters
    ----------
    directory : str, optional
       Path to a directory to write the files to.
    prefix : str, optional
       A prefix to the temporary filename
    suffix : str, optional
       A suffix to the temporary filename

    """
    return tempfile.mkdtemp(dir=directory, prefix=prefix, suffix=suffix)


def tmp_file(delete=False, directory=None, prefix="tmp", stem=None, suffix=""):
    """Return a filename for a temporary file

    The naming convention of scripts will be ``prefix`` + ``stem`` + ``suffix``.

    Parameters
    ----------
    delete : bool, optional
       Delete the file, thus return name only [default: True]
    directory : str, optional
       Path to a directory to write the files to
    prefix : str, optional
       A prefix to the temporary filename
    stem : str, optional
       The steam part of the script name
    suffix : str, optional
       A suffix to the temporary filename

    """
    if directory is None:
        directory = tempfile.gettempdir()
    if stem is None:
        tmpf = tempfile.NamedTemporaryFile(delete=delete, dir=directory, prefix=prefix, suffix=suffix)
        tmpf.close()
        return tmpf.name
    else:
        tmpf = os.path.join(directory, prefix + stem + suffix)
        if not delete:
            open(tmpf, 'w').close()
        return tmpf

