import logging
import uuid

from pyjob.cexec import cexec
from pyjob.exception import PyJobError, PyJobExecutableNotFoundError
from pyjob.script import Script
from pyjob.task import ClusterTask

logger = logging.getLogger(__name__)


class SlurmTask(ClusterTask):
    """Slurm executable :obj:`~pyjob.task.Task`"""

    JOB_ARRAY_INDEX = "$SLURM_ARRAY_TASK_ID"
    SCRIPT_DIRECTIVE = "#SBATCH"

    @property
    def info(self):
        """:obj:`~pyjob.slurm.SlurmTask` information"""
        if self.pid is None:
            return {}
        try:
            cexec(["squeue", "-j", str(self.pid)])
        except (PyJobExecutableNotFoundError, Exception):
            return {}
        else:
            return {"job_number": self.pid, "status": "Running"}

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.slurm.SlurmTask`"""
        if self.pid is None:
            return
        cexec(["scancel", str(self.pid)])
        logger.debug("Terminated task: %d", self.pid)

    def _check_requirements(self):
        """Check if the requirements for task execution are met"""
        self._ensure_exec_available("squeue")

    def _run(self):
        """Method to initialise :obj:`~pyjob.slurm.SlurmTask` execution"""
        self.runscript = self._create_runscript()
        self.runscript.write()
        stdout = cexec(["sbatch", self.runscript.path], cwd=self.directory)
        self.pid = int(stdout.strip().split()[-1])
        logger.debug(
            "%s [%d] submission script is %s",
            self.__class__.__qualname__,
            self.pid,
            self.runscript.path,
        )

    def _create_runscript(self):
        """Utility method to create runscript"""
        runscript = Script(
            directory=self.directory,
            prefix="slurm_",
            suffix=".script",
            stem=str(uuid.uuid1().int),
        )
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + " --export=ALL")
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + f" --job-name={self.name}")
        if self.dependency:
            cmd = f'--depend=afterok:{":".join(map(str, self.dependency))}'
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.queue:
            cmd = f"-p {self.queue}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.nprocesses:
            cmd = f"-n {self.nprocesses}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.directory:
            cmd = f"--chdir={self.directory}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.runtime:
            cmd = f"-t {self.runtime}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.extra:
            cmd = " ".join(map(str, self.extra))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if len(self.script) > 1:
            logf = runscript.path.replace(".script", ".log")
            jobsf = runscript.path.replace(".script", ".jobs")
            with open(jobsf, "w") as f_out:
                f_out.write("\n".join(self.script))
            cmd = f"--array=1-{len(self.script)}%{self.max_array_size}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + f" -o {logf}")
            runscript.extend(self.get_array_bash_extension(jobsf, 0))
        else:
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + f" -o {self.log[0]}")
            runscript.append(self.script[0])
        return runscript
