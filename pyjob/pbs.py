import logging
import re
import uuid

from pyjob.cexec import cexec
from pyjob.exception import PyJobError, PyJobExecutableNotFoundError
from pyjob.script import Script
from pyjob.task import ClusterTask

logger = logging.getLogger(__name__)

RE_LINE_SPLIT_1 = re.compile(r":\\s+")
RE_LINE_SPLIT_2 = re.compile(r"\\s+=\\s+")


class PortableBatchSystemTask(ClusterTask):
    """PortableBatchSystem executable :obj:`~pyjob.task.Task`"""

    JOB_ARRAY_INDEX = "$PBS_ARRAYID"
    SCRIPT_DIRECTIVE = "#PBS"

    @property
    def info(self):
        """:obj:`~pyjob.pbs.PortableBatchSystemTask` information"""
        if self.pid is None:
            return {}
        try:
            stdout = cexec(["qstat", "-f", str(self.pid)], permit_nonzero=True)
        except PyJobExecutableNotFoundError:
            return {}
        all_lines = stdout.splitlines()
        data = {}
        key, job_id = RE_LINE_SPLIT_1.split(all_lines[0], 1)
        data[key] = job_id
        for line in all_lines[1:]:
            line = line.strip()
            if "Unknown queue destination" in line:
                return data
            else:
                kv = RE_LINE_SPLIT_2.split(line, 1)
                if len(kv) == 2:
                    data[kv[0]] = kv[1]
        return data

    def _check_requirements(self):
        """Check if the requirements for task execution are met"""
        self._ensure_exec_available("qstat")

    def kill(self):
        """Immediately terminate the :obj:`~pyjob.pbs.PortableBatchSystemTask`"""
        if self.pid is None:
            return
        cexec(["qdel", str(self.pid)])
        logger.debug("Terminated task: %d", self.pid)

    def _run(self):
        """Method to initialise :obj:`~pyjob.pbs.PortableBatchSystemTask` execution"""
        self.runscript = self._create_runscript()
        self.runscript.write()
        self.pid = cexec(["qsub", self.runscript.path], cwd=self.directory)
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
            prefix="pbs_",
            suffix=".script",
            stem=str(uuid.uuid1().int),
        )
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + " -V")
        runscript.append(self.__class__.SCRIPT_DIRECTIVE + f" -N {self.name}")
        if self.directory:
            cmd = f"-w {self.directory}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.priority:
            cmd = f"-p {self.priority}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.queue:
            cmd = f"-q {self.queue}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.runtime:
            cmd = f"-l walltime={self.get_time(self.runtime)}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.shell:
            cmd = f"-S {self.shell}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.nprocesses:
            cmd = f"-n {self.nprocesses}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if self.extra:
            cmd = " ".join(map(str, self.extra))
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
        if len(self.script) > 1:
            logf = runscript.path.replace(".script", ".log")
            jobsf = runscript.path.replace(".script", ".jobs")
            with open(jobsf, "w") as f_out:
                f_out.write("\n".join(self.script))
            cmd = f"-t 1-{len(self.script)}%{self.max_array_size}"
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + " " + cmd)
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + f" -o {logf}")
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + f" -e {logf}")
            runscript.extend(self.get_array_bash_extension(jobsf, 0))
        else:
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + f" -o {self.log[0]}")
            runscript.append(self.__class__.SCRIPT_DIRECTIVE + f" -e {self.log[0]}")
            runscript.append(self.script[0])
        return runscript
