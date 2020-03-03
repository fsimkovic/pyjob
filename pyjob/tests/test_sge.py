__author__ = 'Felix Simkovic'

import os
import pytest
from unittest import mock

from pyjob.exception import PyJobError
from pyjob.sge import SunGridEngineTask, SGEConfigParameter


class MockSunGridEngineTask(SunGridEngineTask):

    def get_sge_avail_configs(cls, param):
        """Override :py:func:`~pyjob.ClusterTask.get_sge_avail_configs` for testing purposes"""

        if SGEConfigParameter(param) == SGEConfigParameter.ENVIRONMENT:
            config = ['mpi', 'openmpi', 'mpe']
        elif SGEConfigParameter(param) == SGEConfigParameter.QUEUE:
            config = ['low.q', 'medium.q', 'high.q']
        else:
            raise ValueError('Requested SGE parameter is not supported!')

        cls._sge_avail_configs_by_env[param] = set(config)
        return cls._sge_avail_configs_by_env[param]


@pytest.mark.skipif(pytest.on_windows, reason='Unavailable on Windows')
class TestCreateRunscript(object):

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_1(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_2(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -t 1-3 -tc 3',
            '#$ -o {}'.format(logf),
            'script=$(awk "NR==$SGE_TASK_ID" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            '$script > $log 2>&1',
        ]
        assert jobs == paths

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_3(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, max_array_size=1)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -t 1-3 -tc 1',
            '#$ -o {}'.format(logf),
            'script=$(awk "NR==$SGE_TASK_ID" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            '$script > $log 2>&1',
        ]
        assert jobs == paths

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_4(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, name='foobar')
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N foobar',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_5(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, processes=5)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -pe mpi 5',
            '#$ -wd ' + os.getcwd(),
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_6(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, queue='barfoo')
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -q barfoo',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_7(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, directory='..')
        runscript = task._create_runscript()
        wd = os.path.abspath(os.path.join(os.getcwd(), '..'))
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -pe mpi 1',
            '#$ -wd ' + wd,
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_8(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, dependency=[1, 3, 2])
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -hold_jid 1,3,2',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_9(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, runtime=120)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -l h_rt=02:00:00',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_10(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, shell='/bin/csh')
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -S /bin/csh',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_11(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, priority=-1)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -p -1',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.sge.SunGridEngineTask._check_requirements')
    def test_12(self, check_requirements_mock):
        check_requirements_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SunGridEngineTask(paths, extra=['-l mem=100', '-r yes'])
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#$ -V',
            '#$ -w e',
            '#$ -j yes',
            '#$ -N pyjob',
            '#$ -pe mpi 1',
            '#$ -wd ' + os.getcwd(),
            '#$ -l mem=100 -r yes',
            '#$ -o ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    @mock.patch('pyjob.task.ClusterTask._ensure_exec_available')
    def test_13(self, ensure_exec_mock):
        ensure_exec_mock.return_value = None
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]

        with pytest.raises(PyJobError):
            task = MockSunGridEngineTask(paths, extra=['-l mem=100', '-r yes'], environment='dummy-environment',
                                         queue='low.q')
        with pytest.raises(PyJobError):
            task = MockSunGridEngineTask(paths, extra=['-l mem=100', '-r yes'], environment='mpi',
                                         queue='dummy-queue')

        task = MockSunGridEngineTask(paths, extra=['-l mem=100', '-r yes'], environment='mpi', queue='medium.q')
