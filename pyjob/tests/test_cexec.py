__author__ = 'Felix Simkovic'

import os
import pytest
import sys

from pyjob.cexec import cexec
from pyjob.exception import PyJobExecutableNotFoundError, PyJobExecutionError


class TestCexec(object):
    def test_1(self):
        stdout = cexec([sys.executable, '-c', 'import sys; print("hello"); sys.exit(0)'])
        assert stdout == 'hello'

    def test_2(self):
        with pytest.raises(PyJobExecutionError):
            cexec([sys.executable, '-c', 'import sys; sys.exit(1)'])

    def test_3(self):
        cmd = [sys.executable, '-c', 'import sys; print("hello"); sys.exit(1)']
        stdout = cexec(cmd, permit_nonzero=True)
        assert stdout == 'hello'

    def test_4(self):
        if sys.version_info < (3, 0):
            cmd = [sys.executable, '-c', 'import sys; print(raw_input()); sys.exit(0)']
        else:
            cmd = [sys.executable, '-c', 'import sys; print(input()); sys.exit(0)']
        stdout = cexec(cmd, stdin='hello')
        assert stdout == 'hello'

    def test_5(self):
        cmd = [sys.executable, '-c', 'import os, sys; print(os.getcwd()); sys.exit(0)']
        directory = os.path.join(os.getcwd())
        stdout = cexec(cmd, cwd=directory)
        assert stdout == directory

    def test_6(self):
        cmd = [sys.executable, '-c', 'import sys; print("hello"); sys.exit(0)']
        fname = 'test.log'
        with open(fname, 'w') as f:
            stdout = cexec(cmd, stdout=f)
        assert stdout is None
        with open(fname, 'r') as f:
            assert f.read().strip() == 'hello'
        pytest.helpers.unlink([fname])

    def test_7(self):
        cmd = [sys.executable, '-c', 'import os, sys; print(os.getcwd()); sys.exit("error message")']
        directory = os.path.join(os.getcwd())
        with open('stdout.log', 'w') as fstdout, open('stderr.log', 'w') as fstderr:
            stdout = cexec(cmd, stdout=fstdout, stderr=fstderr, permit_nonzero=True)
        assert stdout is None
        with open('stdout.log', 'r') as f:
            assert f.read().strip() == directory
        with open('stderr.log', 'r') as f:
            assert f.read().strip() == 'error message'
        pytest.helpers.unlink(['stdout.log', 'stderr.log'])

    @pytest.mark.skip(reason='disabled')
    def test_8(self):
        with pytest.raises(PyJobExecutableNotFoundError):
            cexec(['fjezfsdkj'])
