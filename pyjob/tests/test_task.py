__author__ = 'Felix Simkovic'

import os

from pyjob.local import CPU_COUNT, LocalTask
from pyjob.script import Script

TEMPLATE = """
def fib(n):
    cache = [0, 1]
    for i in range(n):
        cache.append(cache[-2] + cache[1])
    return cache[-1]
n = {}; print('%dth fib is: %d' % (n, fib(n)))
"""


def get_py_script(i, target):
    script = Script(
        shebang='#!/usr/bin/env python',
        prefix='pyjob',
        stem='test{}'.format(i),
        suffix='.py')
    script.content.extend(TEMPLATE.format(target).split(os.linesep))
    return script


class TestLocalPerformance(object):
    def test_1(self):
        scripts = [get_py_script(i, 1000) for i in range(4)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
        for path, log in zip(paths, logs):
            assert os.path.isfile(log)
        map(os.unlink, paths + logs)
