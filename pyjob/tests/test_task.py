__author__ = 'Felix Simkovic'

import os
import pytest

from pyjob.exception import PyJobError, PyJobTaskLockedError
from pyjob.script import ScriptCollector
from pyjob.task import Task, ClusterTask


class MockTask(Task):
    @property
    def info(self):
        return {}

    def close(self):
        pass

    def kill(self):
        pass

    def _run(self):
        pass


class MockClusterTask(ClusterTask, MockTask):
    JOB_ARRAY_INDEX = '$TEST'
    SCRIPT_DIRECTIVE = '#TEST'

    def _create_runscript(self):
        pass


class TestTask(object):
    def test_1(self):
        task = MockTask(None)
        assert task.pid is None
        assert not task.completed
        assert task.directory == os.getcwd()
        assert task.nprocesses == 1
        assert task.script == []
        assert not task.locked
        assert task.info == {}
        assert task.log == []

    def test_2(self):
        task = MockTask(None, directory='..')
        assert task.directory == os.path.abspath('..')
        assert task.pid is None
        assert not task.completed
        assert task.nprocesses == 1
        assert task.script == []
        assert not task.locked
        assert task.info == {}
        assert task.log == []

    def test_3(self):
        task = MockTask(None, processes=2)
        assert task.nprocesses == 2
        assert task.pid is None
        assert not task.completed
        assert task.directory == os.getcwd()
        assert task.script == []
        assert not task.locked
        assert task.info == {}
        assert task.log == []

    def test_4(self):
        task = MockTask(None)
        assert not task.locked
        with pytest.raises(PyJobError):
            task.run()
        assert not task.locked

    def test_5(self):
        task = MockTask(None)
        task.lock()
        assert task.locked
        with pytest.raises(PyJobTaskLockedError):
            task.run()

    def test_6(self):
        script = pytest.helpers.get_py_script(0, 1)
        task = MockTask(script)
        assert not task.locked
        task.run()
        assert task.locked
        with pytest.raises(PyJobTaskLockedError):
            task.run()
        pytest.helpers.unlink(task.script)

    def test_7(self):
        task = MockTask(None)
        assert not task.locked
        with pytest.raises(PyJobError):
            task.run()
        script = pytest.helpers.get_py_script(0, 1)
        task.add_script(script)
        task.run()
        pytest.helpers.unlink(task.script)

    def test_8(self):
        script = pytest.helpers.get_py_script(0, 1)
        task = MockTask(script)
        assert task.log == [script.path.replace('.py', '.log')]
        pytest.helpers.unlink(task.script)

    def test_9(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        [s.write() for s in scripts]
        task = MockTask([s.path for s in scripts])
        assert task.log == [s.replace('.py', '.log') for s in task.script]
        pytest.helpers.unlink(task.script)

    def test_10(self):
        task = MockTask([])
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        for s in scripts:
            task.add_script(s)
        assert task.script == [s.path for s in scripts]
        pytest.helpers.unlink(task.script)

    def test_11(self):
        container = ScriptCollector(None)
        task = MockTask(container)
        assert task.script_collector is container

    def test_12(self):
        container = ScriptCollector(None)
        task = MockTask(container)
        assert task.script_collector is container
        assert len(task.script_collector) == 0
        task.add_script(pytest.helpers.get_py_script(0, 1))
        assert len(task.script_collector) == 1

    def test_13(self):
        container = ScriptCollector(pytest.helpers.get_py_script(10, 1))
        task = MockTask(container)
        task.add_script([pytest.helpers.get_py_script(i, 1) for i in range(5)])
        assert len(task.script_collector) == 6

    def test_14(self):
        container = ScriptCollector(pytest.helpers.get_py_script(10, 1))
        task = MockTask(container)
        assert len(task.script_collector) == 1
        task.lock()
        assert task.locked
        with pytest.raises(PyJobError):
            task.add_script(pytest.helpers.get_py_script(1, 1))
        assert len(task.script_collector) == 1


@pytest.mark.skipif(pytest.on_windows, reason='Unavailable on Windows')
class TestClusterTask(object):
    def test_get_array_bash_extension_1(self):
        task = MockClusterTask(None)
        fname = 'test.jobs'
        with open(fname, 'w') as f:
            pass
        assert task.get_array_bash_extension(fname, 0) == [
            'script=$(awk "NR==$TEST" test.jobs)', 'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            '$script > $log 2>&1'
        ]
        pytest.helpers.unlink([fname])

    def test_get_array_bash_extension_2(self):
        task = MockClusterTask(None)
        fname = 'test.jobs'
        with open(fname, 'w') as f:
            pass
        assert task.get_array_bash_extension(fname, 1) == [
            'script=$(awk "NR==$(($TEST + 1))" test.jobs)', 'log=$(echo $script | sed "s/\\.${script##*.}/\\.log/")',
            '$script > $log 2>&1'
        ]
        pytest.helpers.unlink([fname])

    def test_get_array_bash_extension_3(self):
        task = MockClusterTask(None)
        with pytest.raises(ValueError):
            task.get_array_bash_extension(None, 1)

    def test_get_array_bash_extension_4(self):
        task = MockClusterTask(None)
        with pytest.raises(ValueError):
            task.get_array_bash_extension('/some/file', 0)

    def test_get_array_bash_extension_5(self):
        task = MockClusterTask(None)
        fname = 'test.jobs'
        with open(fname, 'w') as f:
            pass
        with pytest.raises(ValueError):
            task.get_array_bash_extension(fname, -1)
        pytest.helpers.unlink([fname])
