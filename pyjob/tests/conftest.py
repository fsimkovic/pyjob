__author__ = 'Felix Simkovic'

import os
import pytest
pytest_plugins = ['helpers_namespace']

from pyjob.script import Script

TEMPLATE = """
def fib(n):
    cache = [0, 1]
    if n == 1:
        return cache[0]
    for i in range(n - 2):
        tmp = cache[0]
        cache[0] = cache[1]
        cache[1] += tmp
    return cache[1]
"""


@pytest.helpers.register
def fibonacci(n):
    exec (TEMPLATE)
    return fib(n)


@pytest.helpers.register
def get_py_script(i, target):
    script = Script(shebang='#!/usr/bin/env python', prefix='pyjob', stem='test{}'.format(i), suffix='.py')
    script.content.extend(TEMPLATE.split(os.linesep))
    script.content.append("n = {}; print('%dth fib is: %d' % (n, fib(n)))".format(target))
    return script


@pytest.helpers.register
def unlink(paths):
    for p in paths:
        if os.path.isfile(p):
            os.unlink(p)
