import os

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
