__author__ = 'Felix Simkovic'

import os
import pytest
import sys
import time

from pyjob.exception import PyJobError
from pyjob.local import CPU_COUNT, LocalTask


@pytest.mark.skipif(pytest.on_windows, reason='Deadlock on Windows')
class TestLocalTaskTermination(object):
    def test_terminate_1(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        task = LocalTask(paths, processes=CPU_COUNT)
        task.run()
        task.wait()
        assert all(os.path.isfile(f) for f in logs)
        pytest.helpers.unlink(paths + logs)

    def test_terminate_2(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(4)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        task = LocalTask(paths, processes=CPU_COUNT)
        task.run()
        task.close()
        assert all(os.path.isfile(f) for f in logs)
        pytest.helpers.unlink(paths + logs)

    def test_terminate_3(self):
        scripts = [pytest.helpers.get_py_script(i, 1000000) for i in range(10)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        task = LocalTask(paths, processes=min(CPU_COUNT, 2))
        task.run()
        assert not all(os.path.isfile(f) for f in logs)
        task.close()
        assert all(os.path.isfile(f) for f in logs)
        pytest.helpers.unlink(paths + logs)

    def test_terminate_4(self):
        scripts = [pytest.helpers.get_py_script(i, 1000000) for i in range(5)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]

        def innerf():
            task = LocalTask(paths, processes=min(CPU_COUNT, 2))
            task.run()

        innerf()
        pytest.helpers.unlink(paths + logs)

    # ---- code works but cannot catch correctly raised exception ---- #
    #  def test_terminate_5(self):
    #      scripts = [pytest.helpers.get_py_script(i, 1000000) for i in range(10)]
    #      [s.write() for s in scripts]
    #      paths = [s.path for s in scripts]
    #      logs = [s.path.replace('.py', '.log') for s in scripts]
    #      with LocalTask(paths, processes=min(CPU_COUNT, 2)) as task:
    #          with pytest.raises(PyJobError):
    #              task.run()
    #              pytest.helpers.unlink(paths[4:])
    #      pytest.helpers.unlink(paths[:4] + logs)

    def test_terminate_6(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(100)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
            time.sleep(1)
            task.kill()
        assert all(os.path.isfile(path) for path in paths)
        assert any(os.path.isfile(log) for log in logs)
        assert not all(os.path.isfile(log) for log in logs)
        pytest.helpers.unlink(paths + logs)

    def test_terminate_7(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(10000)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=min(CPU_COUNT, 2)) as task:
            task.run()
            time.sleep(5)
            task.kill()
        assert all(os.path.isfile(path) for path in paths)
        assert any(os.path.isfile(log) for log in logs)
        assert not all(os.path.isfile(log) for log in logs)
        pytest.helpers.unlink(paths + logs)


@pytest.mark.skipif(sys.platform.startswith('win'), reason='Deadlock on Windows')
class TestLocalPerformance(object):
    def test_performance_1(self):
        scripts = [pytest.helpers.get_py_script(i, 1000) for i in range(4)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
        for path, log in zip(paths, logs):
            assert os.path.isfile(log)
        pytest.helpers.unlink(paths + logs)

    def test_performance_2(self):
        scripts = [pytest.helpers.get_py_script(i, 1000) for i in range(16)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in logs)
        pytest.helpers.unlink(paths + logs)

    def test_performance_3(self):
        scripts = [pytest.helpers.get_py_script(i, 1000) for i in range(32)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in logs)
        pytest.helpers.unlink(paths + logs)

    def test_performance_4(self):
        scripts = [pytest.helpers.get_py_script(i, 10000) for i in range(64)]
        [s.write() for s in scripts]
        paths = [s.path for s in scripts]
        logs = [s.path.replace('.py', '.log') for s in scripts]
        with LocalTask(paths, processes=CPU_COUNT) as task:
            task.run()
        assert all(os.path.isfile(f) for f in logs)
        pytest.helpers.unlink(paths + logs)
