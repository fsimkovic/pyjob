__author__ = 'Felix Simkovic'

import os
import pytest
import sys
import time

from pyjob.exception import PyJobError, PyJobTaskLockedError
from pyjob.local import CPU_COUNT, LocalTask


class TestLocalTaskTermination(object):
    @pytest.mark.skipif(pytest.on_windows, reason='Deadlock on Windows')
    def test_terminate_1(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        task = LocalTask(scripts, processes=CPU_COUNT)
        task.run()
        task.wait()
        for f in task.log:
            assert os.path.isfile(f)
        pytest.helpers.unlink(task.script + task.log)

    def test_terminate_2(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        task = LocalTask(scripts, processes=CPU_COUNT)
        task.run()
        task.close()
        for f in task.log:
            assert os.path.isfile(f)
        pytest.helpers.unlink(task.script + task.log)

    @pytest.mark.skipif(pytest.on_windows, reason='Deadlock on Windows')
    def test_terminate_3(self):
        scripts = [pytest.helpers.get_py_script(i, 1000000) for i in range(4)]
        task = LocalTask(scripts, processes=min(CPU_COUNT, 2))
        task.run()
        assert not all(os.path.isfile(f) for f in task.log)
        task.close()
        assert all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)

    @pytest.mark.skipif(pytest.on_windows, reason='Deadlock on Windows')
    def test_terminate_4(self):
        scripts = [pytest.helpers.get_py_script(i, 1000000) for i in range(5)]
        files = []

        def innerf():
            task = LocalTask(scripts, processes=min(CPU_COUNT, 2))
            task.run()
            files.extend(task.script + task.log)

        innerf()
        pytest.helpers.unlink(files)

    @pytest.mark.skip(reason='Unstable test')
    def test_terminate_5(self):
        scripts = [pytest.helpers.get_py_script(i, 1000000) for i in range(10)]
        with LocalTask(scripts, processes=min(CPU_COUNT, 2)) as task:
            with pytest.raises(PyJobError):
                task.run()
                pytest.helpers.unlink(task.script[4:])
        pytest.helpers.unlink(task.script[:4] + task.log)

    def test_terminate_6(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(100)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
            time.sleep(1)
            task.kill()
        assert all(os.path.isfile(path) for path in task.script)
        assert any(os.path.isfile(log) for log in task.log)
        assert not all(os.path.isfile(log) for log in task.log)
        pytest.helpers.unlink(task.script + task.log)

    @pytest.mark.skipif(pytest.on_windows, reason='Deadlock on Windows')
    def test_terminate_7(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(10000)]
        with LocalTask(scripts, processes=min(CPU_COUNT, 2)) as task:
            task.run()
            time.sleep(5)
            task.kill()
        assert all(os.path.isfile(path) for path in task.script)
        assert any(os.path.isfile(log) for log in task.log)
        assert not all(os.path.isfile(log) for log in task.log)
        pytest.helpers.unlink(task.script + task.log)

    def test_terminate_8(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        task = LocalTask(scripts, processes=CPU_COUNT)
        task.run()
        task.wait()
        for f in task.log:
            assert os.path.isfile(f)
        with pytest.raises(PyJobTaskLockedError):
            task.run()
        pytest.helpers.unlink(task.script + task.log)

    def test_terminate_9(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        task = LocalTask(scripts, processes=CPU_COUNT)
        task.run()
        with pytest.raises(PyJobTaskLockedError):
            task.run()
        task.wait()
        for f in task.log:
            assert os.path.isfile(f)
        pytest.helpers.unlink(task.script + task.log)


class TestLocalPerformance(object):
    def test_performance_1(self):
        scripts = [pytest.helpers.get_py_script(i, 1000) for i in range(4)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)

    def test_performance_2(self):
        scripts = [pytest.helpers.get_py_script(i, 1000) for i in range(16)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)

    def test_performance_3(self):
        scripts = [pytest.helpers.get_py_script(i, 1000) for i in range(32)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)

    def test_performance_4(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(64)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)
