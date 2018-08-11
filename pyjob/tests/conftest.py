__author__ = 'Felix Simkovic'

import os
import pytest

from pyjob.script import Script

pytest_plugins = ['helpers_namespace']

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


@pytest.helpers.register
def get_py_script(i, target):
    script = Script(shebang='#!/usr/bin/env python', prefix='pyjob', stem='test{}'.format(i), suffix='.py')
    script.content.extend(TEMPLATE.format(target).split(os.linesep))
    return script


@pytest.helpers.register
def unlink(paths):
    for p in paths:
        if os.path.isfile(p):
            os.unlink(p)
