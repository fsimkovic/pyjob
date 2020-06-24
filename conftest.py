import inspect
import os
import random
import string
import sys

import pyjob
pyjob.config = {}

from pyjob.script import Script

pytest_plugins = ["helpers_namespace"]


import pytest

pytest.on_windows = sys.platform.startswith("win")


@pytest.helpers.register
def fibonacci(n):
    cache = [0, 1]
    if n == 1:
        return cache[0]
    for i in range(n - 2):
        tmp = cache[0]
        cache[0] = cache[1]
        cache[1] += tmp
    return cache[1]


@pytest.helpers.register
def get_py_script(i, target):
    script = Script(
        shebang="#!{}".format(sys.executable),
        prefix="pyjob",
        stem="test{}".format(i),
        suffix=".py",
    )
    script.extend(inspect.getsource(fibonacci).splitlines())
    script.pop(0)  # remove decorator
    script.extend(
        [
            "if __name__ == '__main__':",
            "\ttarget = {}".format(target),
            "\tprint('{}th fib is: {}'.format(target, fibonacci(target)))",
        ]
    )
    return script


@pytest.helpers.register
def unlink(paths):
    for p in paths:
        if os.path.isfile(p):
            os.unlink(p)


@pytest.helpers.register
def randomstr(n=5):
    return "".join(random.choice(string.ascii_lowercase) for _ in range(n))
