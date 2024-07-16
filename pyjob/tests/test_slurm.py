import os
from unittest import mock

import pytest
from pyjob.slurm import SlurmTask


@pytest.mark.skipif(pytest.on_windows, reason="Unavailable on Windows")
@mock.patch("pyjob.slurm.SlurmTask._check_requirements")
class TestCreateRunscript(object):
    def test_1(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#SBATCH --export=ALL",
            "#SBATCH --job-name=pyjob",
            "#SBATCH -n 1",
            "#SBATCH --chdir=" + os.getcwd(),
            "#SBATCH -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_2(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths)
        runscript = task._create_runscript()
        logf = runscript.path.replace(".script", ".log")
        jobsf = runscript.path.replace(".script", ".jobs")
        with open(jobsf, "r") as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#SBATCH --export=ALL",
            "#SBATCH --job-name=pyjob",
            "#SBATCH -n 1",
            "#SBATCH --chdir=" + os.getcwd(),
            "#SBATCH --array=1-3%3",
            "#SBATCH -o {}".format(logf),
            'script=$(awk "NR==$SLURM_ARRAY_TASK_ID" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            "$script > $log 2>&1",
        ]
        assert jobs == paths

    def test_3(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, max_array_size=1)
        runscript = task._create_runscript()
        logf = runscript.path.replace(".script", ".log")
        jobsf = runscript.path.replace(".script", ".jobs")
        with open(jobsf, "r") as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#SBATCH --export=ALL",
            "#SBATCH --job-name=pyjob",
            "#SBATCH -n 1",
            "#SBATCH --chdir=" + os.getcwd(),
            "#SBATCH --array=1-3%1",
            "#SBATCH -o {}".format(logf),
            'script=$(awk "NR==$SLURM_ARRAY_TASK_ID" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            "$script > $log 2>&1",
        ]
        assert jobs == paths

    def test_4(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, name="foobar")
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#SBATCH --export=ALL",
            "#SBATCH --job-name=foobar",
            "#SBATCH -n 1",
            "#SBATCH --chdir=" + os.getcwd(),
            "#SBATCH -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_5(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, processes=5)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#SBATCH --export=ALL",
            "#SBATCH --job-name=pyjob",
            "#SBATCH -n 5",
            "#SBATCH --chdir=" + os.getcwd(),
            "#SBATCH -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_6(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, queue="barfoo")
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#SBATCH --export=ALL",
            "#SBATCH --job-name=pyjob",
            "#SBATCH -p barfoo",
            "#SBATCH -n 1",
            "#SBATCH --chdir=" + os.getcwd(),
            "#SBATCH -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_7(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, directory="..")
        runscript = task._create_runscript()
        wd = os.path.abspath(os.path.join(os.getcwd(), ".."))
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#SBATCH --export=ALL",
            "#SBATCH --job-name=pyjob",
            "#SBATCH -n 1",
            "#SBATCH --chdir=" + wd,
            "#SBATCH -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_8(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, dependency=[1, 3, 2])
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#SBATCH --export=ALL",
            "#SBATCH --job-name=pyjob",
            "#SBATCH --depend=afterok:1:3:2",
            "#SBATCH -n 1",
            "#SBATCH --chdir=" + os.getcwd(),
            "#SBATCH -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_9(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, extra=["--mem=100M", "--requeue"])
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#SBATCH --export=ALL",
            "#SBATCH --job-name=pyjob",
            "#SBATCH -n 1",
            "#SBATCH --chdir=" + os.getcwd(),
            "#SBATCH --mem=100M --requeue",
            "#SBATCH -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]
