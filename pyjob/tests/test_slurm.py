__author__ = 'Felix Simkovic'

import os
import pytest

from pyjob.slurm import SlurmTask


class TestCreateRunscript(object):
    def test_1(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths)
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -n 1', '#SBATCH --workdir=' + os.getcwd(),
            '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_2(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -n 1', '#SBATCH --workdir=' + os.getcwd(),
            '#SBATCH --array=1-3%3', '#SBATCH -o {}'.format(logf),
            'script=$(awk "NR==$SLURM_ARRAY_TASK_ID" {})'.format(jobsf), "log=$(echo $script | sed 's/\.sh/\.log/')",
            '$script > $log 2>&1'
        ]
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        assert jobs == paths
        pytest.helpers.unlink(paths + [jobsf])

    def test_3(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(3)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, max_array_size=1)
        runscript = task._create_runscript()
        logf = runscript.path.replace('.script', '.log')
        jobsf = runscript.path.replace('.script', '.jobs')
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -n 1', '#SBATCH --workdir=' + os.getcwd(),
            '#SBATCH --array=1-3%1', '#SBATCH -o {}'.format(logf),
            'script=$(awk "NR==$SLURM_ARRAY_TASK_ID" {})'.format(jobsf), "log=$(echo $script | sed 's/\.sh/\.log/')",
            '$script > $log 2>&1'
        ]
        with open(jobsf, 'r') as f_in:
            jobs = [l.strip() for l in f_in]
        assert jobs == paths
        pytest.helpers.unlink(paths + [jobsf])

    def test_4(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, name='foobar')
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=foobar', '#SBATCH -n 1', '#SBATCH --workdir=' + os.getcwd(),
            '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_5(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, processes=5)
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -n 5', '#SBATCH --workdir=' + os.getcwd(),
            '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_6(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, queue='barfoo')
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -p barfoo', '#SBATCH -n 1',
            '#SBATCH --workdir=' + os.getcwd(), '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_7(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, directory='..')
        runscript = task._create_runscript()
        wd = os.path.abspath(os.path.join(os.getcwd(), '..'))
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -n 1', '#SBATCH --workdir=' + wd,
            '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_8(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, dependency=[1, 3, 2])
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH --depend=afterok:1:3:2', '#SBATCH -n 1',
            '#SBATCH --workdir=' + os.getcwd(), '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)

    def test_9(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, extra=['--mem=100M', '--requeue'])
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -n 1', '#SBATCH --workdir=' + os.getcwd(),
            '#SBATCH --mem=100M --requeue', '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        pytest.helpers.unlink(paths)
