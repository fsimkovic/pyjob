__author__ = 'Felix Simkovic'

import os
import pytest
import sys

from pyjob.lsf import LoadSharingFacilityTask


@pytest.marks.skipif(sys.platform.startswith('win'), msg='Unavailable on Windows')
class TestCreateRunscript(object):
    def test_1(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths)
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + os.getcwd(), '#BSUB -R "span[ptile=1]"',
            '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_2(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + os.getcwd(), '#BSUB -R "span[ptile=1]"', '#BSUB J pyjob[1-3%3]',
            '#BSUB -o {}'.format(logf), 'script=$(awk "NR==$LSB_JOBINDEX" {})'.format(jobsf),
            "log=$(echo $script | sed 's/\.sh/\.log/')", '$script > $log 2>&1'
        ]
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        assert jobs == paths
        pytest.helpers.unlink(paths + [jobsf])

    def test_3(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, max_array_size=1)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + os.getcwd(), '#BSUB -R "span[ptile=1]"', '#BSUB J pyjob[1-3%1]',
            '#BSUB -o {}'.format(logf), 'script=$(awk "NR==$LSB_JOBINDEX" {})'.format(jobsf),
            "log=$(echo $script | sed 's/\.sh/\.log/')", '$script > $log 2>&1'
        ]
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        assert jobs == paths
        pytest.helpers.unlink(paths + [jobsf])

    def test_4(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, name='foobar')
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J foobar', '#BSUB -cwd ' + os.getcwd(), '#BSUB -R "span[ptile=1]"',
            '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_5(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, processes=5)
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + os.getcwd(), '#BSUB -R "span[ptile=5]"',
            '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_6(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, queue='barfoo')
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + os.getcwd(), '#BSUB -q barfoo', '#BSUB -R "span[ptile=1]"',
            '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_7(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, directory='..')
        runscript = task._create_runscript()
        wd = os.path.abspath(os.path.join(os.getcwd(), '..'))
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + wd, '#BSUB -R "span[ptile=1]"',
            '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_8(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, dependency=[1, 3, 2])
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -w deps(1) && deps(3) && deps(2)', '#BSUB -cwd ' + os.getcwd(),
            '#BSUB -R "span[ptile=1]"', '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_9(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, runtime=120)
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + os.getcwd(), '#BSUB -W 120', '#BSUB -R "span[ptile=1]"',
            '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_10(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, shell='/bin/csh')
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + os.getcwd(), '#BSUB -L /bin/csh', '#BSUB -R "span[ptile=1]"',
            '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_11(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, priority=-1)
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + os.getcwd(), '#BSUB -sp -1', '#BSUB -R "span[ptile=1]"',
            '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_12(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = LoadSharingFacilityTask(paths, extra=['-M 100', '-r'])
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#BSUB -J pyjob', '#BSUB -cwd ' + os.getcwd(), '#BSUB -R "span[ptile=1]"', '#BSUB -M 100 -r',
            '#BSUB -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)
