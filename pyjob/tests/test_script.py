__author__ = 'Felix Simkovic'

import os
import pytest
import tempfile

from pyjob.exception import PyJobError
from pyjob.script import Script, ScriptContainer, is_valid_script_path


class TestScriptContainer(object):
    def test_1(self):
        sc = ScriptContainer([])
        assert sc.scripts == []

    def test_2(self):
        script = pytest.helpers.get_py_script(0, 1)
        sc = ScriptContainer(script)
        assert sc.scripts == [script]

    def test_3(self):
        script = pytest.helpers.get_py_script(0, 1)
        script.write()
        sc = ScriptContainer(script.path)
        assert len(sc.scripts) == 1
        assert isinstance(sc.scripts[0], Script)
        pytest.helpers.unlink([script.path])

    def test_4(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptContainer(scripts)
        assert sc.scripts == scripts

    def test_5(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        [s.write() for s in scripts]
        sc = ScriptContainer([s.path for s in scripts])
        assert len(sc.scripts) == 2
        assert all(isinstance(s, Script) for s in sc)
        pytest.helpers.unlink([s.path for s in scripts])

    def test_6(self):
        with pytest.raises(PyJobError):
            ScriptContainer([1])

    def test_7(self):
        with pytest.raises(IOError):
            ScriptContainer(['test'])

    def test_8(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptContainer(scripts[:1])
        sc.add(scripts[1:])
        assert sc.scripts == scripts

    def test_9(self):
        sc = ScriptContainer([])
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc.add(scripts)
        assert sc.scripts == scripts

    def test_10(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptContainer(scripts)
        sc.add([])
        assert sc.scripts == scripts

    def test_11(self):
        scripts1 = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptContainer(scripts1)
        assert sc.scripts == scripts1
        scripts2 = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc.scripts = scripts2
        assert sc.scripts == scripts2

    def test_12(self):
        scripts1 = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptContainer(scripts1)
        assert sc.scripts == scripts1
        sc.scripts = []
        assert sc.scripts == []

    def test_13(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptContainer(scripts)
        assert sc.scripts == scripts
        sc.dump()
        paths = [s.path for s in scripts]
        assert all(os.path.isfile(p) for p in paths)
        pytest.helpers.unlink(paths)


class TestScriptRead(object):
    def test_read_1(self):
        fh = tempfile.NamedTemporaryFile(mode='w', delete=False)
        fh.write('#!/usr/bin/env python\nprint("PyJob is cool!")\n')
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang == '#!/usr/bin/env python'
        assert script.content == ['print("PyJob is cool!")']
        pytest.helpers.unlink([fh.name])

    def test_read_2(self):
        fh = tempfile.NamedTemporaryFile(mode='w', delete=False)
        fh.write('print("PyJob is cool!")\n')
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang is None
        assert script.content == ['print("PyJob is cool!")']
        pytest.helpers.unlink([fh.name])

    def test_read_3(self):
        fh = tempfile.NamedTemporaryFile(mode='w', delete=False)
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang is None
        assert script.content == []
        pytest.helpers.unlink([fh.name])

    def test_read_4(self):
        fh = tempfile.NamedTemporaryFile(mode='w', delete=False)
        fh.write('#!/bin/bash')
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang == '#!/bin/bash'
        assert script.content == []
        pytest.helpers.unlink([fh.name])

    def test_read_5(self):
        fh = tempfile.NamedTemporaryFile(mode='w', delete=False)
        fh.write('\n#!/bin/bash')
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang is None
        assert script.content == ['', '#!/bin/bash']
        pytest.helpers.unlink([fh.name])

    def test_read_6(self):
        fh = tempfile.NamedTemporaryFile(mode='w', dir='.', delete=True, prefix='pyjob', suffix='.sh')
        script = Script.read(fh.name)
        fh.close()
        assert script.directory == os.getcwd()
        assert script.prefix == ''
        assert script.stem[:5] == 'pyjob'
        assert script.suffix == '.sh'


class TestIsValidScriptPath(object):
    def test_is_valid_script_path_1(self):
        fh = tempfile.NamedTemporaryFile(delete=True)
        fh.close()
        assert not is_valid_script_path(fh.name)

    def test_is_valid_script_path_2(self):
        fh = tempfile.NamedTemporaryFile(delete=True)
        assert not is_valid_script_path(fh.name)
        fh.close()

    def test_is_valid_script_path_3(self):
        fh = tempfile.NamedTemporaryFile(delete=True)
        os.chmod(fh.name, 0o777)
        assert is_valid_script_path(fh.name)
        fh.close()
