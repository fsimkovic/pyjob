import os

from pyjob.slurm import SlurmTask
from pyjob.script import Script

TEMPLATE = """
def fib(n):
    cache = [0, 1]
    for i in range(n):
        tmp = cache[0]
        cache[0] = cache[1]
        cache[1] += tmp
    return cache[1]
n = {}; print('%dth fib is: %d' % (n, fib(n)))
"""


def get_py_script(i, target):
    script = Script(shebang='#!/usr/bin/env python', prefix='pyjob', stem='test{}'.format(i), suffix='.py')
    script.content.extend(TEMPLATE.format(target).split(os.linesep))
    return script


class TestCreateRunscript(object):
    def test_1(self):
        scripts = [get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths)
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -n 1', '#SBATCH --workdir=' + os.getcwd(),
            '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        for f in paths:
            os.unlink(f)

    def test_2(self):
        scripts = [get_py_script(i, 1) for i in range(3)]
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
        for f in paths + [jobsf]:
            os.unlink(f)

    def test_3(self):
        scripts = [get_py_script(i, 1) for i in range(3)]
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
        for f in paths + [jobsf]:
            os.unlink(f)

    def test_4(self):
        scripts = [get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, name='foobar')
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=foobar', '#SBATCH -n 1', '#SBATCH --workdir=' + os.getcwd(),
            '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        for f in paths:
            os.unlink(f)

    def test_5(self):
        scripts = [get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, processes=5)
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -n 5', '#SBATCH --workdir=' + os.getcwd(),
            '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        for f in paths:
            os.unlink(f)

    def test_6(self):
        scripts = [get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, queue='barfoo')
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH -p barfoo', '#SBATCH -n 1',
            '#SBATCH --workdir=' + os.getcwd(), '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        for f in paths:
            os.unlink(f)

    def test_7(self):
        scripts = [get_py_script(i, 1) for i in range(1)]
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
        for f in paths:
            os.unlink(f)

    def test_8(self):
        scripts = [get_py_script(i, 1) for i in range(1)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        task = SlurmTask(paths, dependency=[1, 3, 2])
        runscript = task._create_runscript()
        assert runscript.shebang == '#!/bin/bash'
        assert runscript.content == [
            '#SBATCH --export=ALL', '#SBATCH --job-name=pyjob', '#SBATCH --depend=afterok:1:3:2', '#SBATCH -n 1',
            '#SBATCH --workdir=' + os.getcwd(), '#SBATCH -o ' + paths[0].replace('.py', '.log'), paths[0]
        ]
        for f in paths:
            os.unlink(f)
