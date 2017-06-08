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

"""Available platforms"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"
__version__ = "0.1"

import os
import sys
import tempfile

from pyjob.exception import PyJobUnknownPlatform

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
        raise PyJobUnknownPlatform("Unknown platform")


def prep_array_script(scripts, directory, task_env):
    """Prepare multiple jobs to be an array

    Parameters
    ----------
    scripts : list
       The scripts to be run as part of the array
    directory : str
       The directory to create the files in
    task_env : str
       The task environment variable

    Returns
    -------
    str
       The array script
    str
       The file listing all jobs

    """
    # Write all jobs into an array.jobs file
    array_jobs = tempfile.NamedTemporaryFile(delete=False, dir=directory, prefix="array_", suffix=".jobs").name
    with open(array_jobs, 'w') as f_out:
        f_out.write(os.linesep.join(scripts) + os.linesep)
    # Create the actual executable script
    array_script = array_jobs.replace(".jobs", ".script")
    with open(array_script, "w") as f_out:
        # Construct the content for the file
        content = "#!/bin/sh" + os.linesep
        content += 'script=$(awk "NR==$' + task_env + '" ' + array_jobs + ')' + os.linesep
        content += "log=$(echo $script | sed 's/.sh/.log/')" + os.linesep
        content += "$script > $log" + os.linesep
        f_out.write(content)
    return array_script, array_jobs
