"""Container for the most basic platform layout"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"
__version__ = "0.1"

import logging
import os

from pyjob.misc import tmp_fname

logger = logging.getLogger(__name__)


class Platform(object):

    @staticmethod
    def alt(*args, **kwargs):
        logger.debug("Function unavailable for specified queue type")
        return None

    @staticmethod
    def hold(*args, **kwargs):
        logger.debug("Function unavailable for specified queue type")
        return None

    @staticmethod
    def kill(*args, **kwargs):
        logger.debug("Function unavailable for specified queue type")
        return None

    @staticmethod
    def rls(*args, **kwargs):
        logger.debug("Function unavailable for specified queue type")
        return None

    @staticmethod
    def sub(*args, **kwargs):
        logger.debug("Function unavailable for specified queue type")
        return None

    @staticmethod
    def stat(*args, **kwargs):
        logger.debug("Function unavailable for specified queue type")
        return None
    
    @staticmethod
    def prep_array_scripts(scripts, directory, task_env):
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
        array_jobs = tmp_fname(directory=directory, prefix="array_", suffix='.jobs')
        with open(array_jobs, 'w') as f_out:
            f_out.write(os.linesep.join(scripts) + os.linesep)
        # Create the actual executable script
        array_script = array_jobs.replace(".jobs", ".script")
        with open(array_script, "w") as f_out:
            # Construct the content for the file
            content = "#!/bin/sh" + os.linesep
            content += "script=`sed -n \"${" + task_env + "}p\" " + array_jobs + "`" + os.linesep
            content += "log=\"${script%.*}.log\"" + os.linesep
            content += "$script > $log" + os.linesep
            f_out.write(content)
        return array_script, array_jobs

