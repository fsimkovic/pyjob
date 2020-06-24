import os
import pytest
from unittest import mock

from pyjob.lsf import LoadSharingFacilityTask


@pytest.mark.skipif(pytest.on_windows, reason="Unavailable on Windows")
@mock.patch("pyjob.lsf.LoadSharingFacilityTask._check_requirements")
class TestCreateRunscript(object):
    def test_1(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J pyjob",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_2(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths)
        runscript = task._create_runscript()
        logf = runscript.path.replace(".script", ".log")
        jobsf = runscript.path.replace(".script", ".jobs")
        with open(jobsf, "r") as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J pyjob[1-3]%3",
            "#BSUB -o {}".format(logf),
            'script=$(awk "NR==$(($LSB_JOBINDEX + 1))" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            "$script > $log 2>&1",
        ]
        assert jobs == paths

    def test_3(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, max_array_size=1)
        runscript = task._create_runscript()
        logf = runscript.path.replace(".script", ".log")
        jobsf = runscript.path.replace(".script", ".jobs")
        with open(jobsf, "r") as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J pyjob[1-3]%1",
            "#BSUB -o {}".format(logf),
            'script=$(awk "NR==$(($LSB_JOBINDEX + 1))" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            "$script > $log 2>&1",
        ]
        assert jobs == paths

    def test_4(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, name="foobar")
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J foobar",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_5(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, processes=5)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            '#BSUB -R "span[ptile=5]"',
            "#BSUB -J pyjob",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_6(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, queue="barfoo")
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            "#BSUB -q barfoo",
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J pyjob",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_7(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, directory="..")
        runscript = task._create_runscript()
        wd = os.path.abspath(os.path.join(os.getcwd(), ".."))
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + wd,
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J pyjob",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_8(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, dependency=[1, 3, 2])
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -w deps(1) && deps(3) && deps(2)",
            "#BSUB -cwd " + os.getcwd(),
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J pyjob",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_9(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, runtime=120)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            "#BSUB -W 120",
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J pyjob",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_10(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, shell="/bin/csh")
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            "#BSUB -L /bin/csh",
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J pyjob",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_11(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, priority=-1)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            "#BSUB -sp -1",
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -J pyjob",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]

    def test_12(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, extra=["-M 100", "-r"])
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == "#!/bin/bash"
        assert runscript.content == [
            "#BSUB -cwd " + os.getcwd(),
            '#BSUB -R "span[ptile=1]"',
            "#BSUB -M 100 -r",
            "#BSUB -J pyjob",
            "#BSUB -o " + paths[0].replace(".py", ".log"),
            paths[0],
        ]
