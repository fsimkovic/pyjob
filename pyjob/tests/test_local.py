import os
import pytest
import sys
import time

from pyjob.exception import PyJobError, PyJobTaskLockedError
from pyjob.local import CPU_COUNT, LocalTask


@pytest.mark.skipif(pytest.on_windows, reason="Deadlock on Windows")
class TestLocalTaskTermination(object):
    def test_terminate_1(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        task = LocalTask(scripts, processes=CPU_COUNT)
        task.run()
        task.wait()
        all_found = all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)
        assert all_found

    def test_terminate_2(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        task = LocalTask(scripts, processes=CPU_COUNT)
        task.run()
        task.close()
        all_found = all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)
        assert all_found

    def test_terminate_3(self):
        scripts = [pytest.helpers.get_py_script(i, 1000000) for i in range(4)]
        task = LocalTask(scripts, processes=min(CPU_COUNT, 2))
        task.run()
        not_all_found = not all(os.path.isfile(f) for f in task.log)
        task.close()
        all_found = all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)
        assert not_all_found and all_found

    def test_terminate_4(self):
        scripts = [pytest.helpers.get_py_script(i, 1000000) for i in range(5)]
        files = []

        def innerf():
            task = LocalTask(scripts, processes=min(CPU_COUNT, 2))
            task.run()
            files.extend(task.script + task.log)

        innerf()
        pytest.helpers.unlink(files)

    @pytest.mark.skip(reason="Unstable test")
    def test_terminate_5(self):
        scripts = [pytest.helpers.get_py_script(i, 1000000) for i in range(10)]
        with LocalTask(scripts, processes=min(CPU_COUNT, 2)) as task:
            with pytest.raises(PyJobError):
                task.run()
                pytest.helpers.unlink(task.script[4:])
        pytest.helpers.unlink(task.script[:4] + task.log)

    def test_terminate_6(self):
        scripts = [pytest.helpers.get_py_script(i, 50000) for i in range(100)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
            time.sleep(1)
            task.kill()
        all_scripts_found = all(os.path.isfile(path) for path in task.script)
        some_logs_found = any(os.path.isfile(log) for log in task.log) and not all(
            os.path.isfile(log) for log in task.log
        )
        pytest.helpers.unlink(task.script + task.log)
        assert all_scripts_found and some_logs_found

    def test_terminate_7(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(10000)]
        with LocalTask(scripts, processes=min(CPU_COUNT, 2)) as task:
            task.run()
            time.sleep(5)
            task.kill()
        all_scripts_found = all(os.path.isfile(path) for path in task.script)
        some_logs_found = any(os.path.isfile(log) for log in task.log) and not all(
            os.path.isfile(log) for log in task.log
        )
        pytest.helpers.unlink(task.script + task.log)
        assert all_scripts_found and some_logs_found

    def test_terminate_8(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        task = LocalTask(scripts, processes=CPU_COUNT)
        task.run()
        task.wait()
        all_found = all(os.path.isfile(f) for f in task.log)
        with pytest.raises(PyJobTaskLockedError):
            task.run()
        pytest.helpers.unlink(task.script + task.log)
        assert all_found

    def test_terminate_9(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        task = LocalTask(scripts, processes=CPU_COUNT)
        task.run()
        with pytest.raises(PyJobTaskLockedError):
            task.run()
        task.wait()
        all_found = all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)
        assert all_found


@pytest.mark.skipif(pytest.on_windows, reason="Deadlock on Windows")
class TestLocalPerformance(object):
    def test_performance_1(self):
        scripts = [pytest.helpers.get_py_script(i, 1000) for i in range(4)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
        all_found = all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)
        assert all_found

    def test_performance_2(self):
        scripts = [pytest.helpers.get_py_script(i, 1000) for i in range(16)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
        all_found = all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)
        assert all_found

    def test_performance_3(self):
        scripts = [pytest.helpers.get_py_script(i, 1000) for i in range(32)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
        all_found = all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)
        assert all_found

    def test_performance_4(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(64)]
        with LocalTask(scripts, processes=CPU_COUNT) as task:
            task.run()
        all_found = all(os.path.isfile(f) for f in task.log)
        pytest.helpers.unlink(task.script + task.log)
        assert all_found
