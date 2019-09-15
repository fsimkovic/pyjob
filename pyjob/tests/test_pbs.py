__author__ = 'Felix Simkovic'

import os
import pytest

from pyjob.pbs import PortableBatchSystemTask


@pytest.mark.skipif(pytest.on_windows, reason='Unavailable on Windows')
class TestCreateRunscript(object):
    def test_1(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_2(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -t 1-3%3',
            '#PBS -o {}'.format(logf),
            '#PBS -e {}'.format(logf),
            'script=$(awk "NR==$PBS_ARRAYID" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            '$script > $log 2>&1',
        ]
        assert jobs == paths

    def test_3(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths, max_array_size=1)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        pytest.helpers.unlink(paths + [jobsf])
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -t 1-3%1',
            '#PBS -o {}'.format(logf),
            '#PBS -e {}'.format(logf),
            'script=$(awk "NR==$PBS_ARRAYID" {})'.format(jobsf),
            'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            '$script > $log 2>&1',
        ]
        assert jobs == paths

    def test_4(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths, name='foobar')
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N foobar',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_5(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths, processes=5)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 5',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_6(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths, queue='barfoo')
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -q barfoo',
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_7(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths, directory='..')
        runscript = task._create_runscript()
        wd = os.path.abspath(os.path.join(os.getcwd(), '..'))
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + wd,
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_8(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths, runtime=120)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -l walltime=02:00:00',
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_9(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths, shell='/bin/csh')
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -S /bin/csh',
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_10(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths, priority=-1)
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -p -1',
            '#PBS -n 1',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]

    def test_11(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = PortableBatchSystemTask(paths, extra=['-l mem=100', '-r y'])
        runscript = task._create_runscript()
        pytest.helpers.unlink(paths)
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#PBS -V',
            '#PBS -N pyjob',
            '#PBS -w ' + os.getcwd(),
            '#PBS -n 1',
            '#PBS -l mem=100 -r y',
            '#PBS -o ' + paths[0].replace('.py', '.log'),
            '#PBS -e ' + paths[0].replace('.py', '.log'),
            paths[0],
        ]
