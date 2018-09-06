__author__ = 'Felix Simkovic'

import os
import pytest
import tempfile

from pyjob.exception import PyJobError
from pyjob.script import Script
from pyjob.script import ScriptCollector
from pyjob.script import ScriptProperty
from pyjob.script import LocalScriptCreator
from pyjob.script import is_valid_script_path


class TestScriptCollector(object):
    def test_1(self):
        sc = ScriptCollector([])
        assert sc.scripts == []

    def test_2(self):
        sc = ScriptCollector(None)
        assert sc.scripts == []

    def test_3(self):
        script = pytest.helpers.get_py_script(0, 1)
        sc = ScriptCollector(script)
        assert sc.scripts == [script]

    def test_4(self):
        script = pytest.helpers.get_py_script(0, 1)
        script.write()
        sc = ScriptCollector(script.path)
        assert len(sc.scripts) == 1
        assert isinstance(sc.scripts[0], Script)
        pytest.helpers.unlink([script.path])

    def test_5(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptCollector(scripts)
        assert sc.scripts == scripts

    def test_6(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        [s.write() for s in scripts]
        sc = ScriptCollector([s.path for s in scripts])
        assert len(sc.scripts) == 2
        assert all(isinstance(s, Script) for s in sc)
        pytest.helpers.unlink([s.path for s in scripts])

    def test_7(self):
        with pytest.raises(PyJobError):
            ScriptCollector([1])

    def test_8(self):
        with pytest.raises(ValueError):
            ScriptCollector(['test'])

    def test_9(self):
        with pytest.raises(IOError):
            ScriptCollector(['test.sh'])

    def test_10(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptCollector(scripts[:1])
        sc.add(scripts[1:])
        assert sc.scripts == scripts

    def test_11(self):
        sc = ScriptCollector([])
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc.add(scripts)
        assert sc.scripts == scripts

    def test_12(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptCollector(scripts)
        sc.add([])
        assert sc.scripts == scripts

    def test_13(self):
        scripts1 = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptCollector(scripts1)
        assert sc.scripts == scripts1
        scripts2 = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc.scripts = scripts2
        assert sc.scripts == scripts2

    def test_14(self):
        scripts1 = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptCollector(scripts1)
        assert sc.scripts == scripts1
        sc.scripts = []
        assert sc.scripts == []

    def test_15(self):
        scripts = [pytest.helpers.get_py_script(i, 1) for i in range(2)]
        sc = ScriptCollector(scripts)
        assert sc.scripts == scripts
        sc.dump()
        paths = [s.path for s in scripts]
        assert all(os.path.isfile(p) for p in paths)
        pytest.helpers.unlink(paths)

    def test_16(self):
        with pytest.raises(ValueError):
            Script(suffix=None)

    def test_17(self):
        with pytest.raises(ValueError):
            Script(suffix='')

    def test_18(self):
        with pytest.raises(ValueError):
            Script(suffix='x')

    def test_19(self):
        with pytest.raises(ValueError):
            Script(suffix=',x')

    def test_20(self):
        script = Script()
        script.append('test line')
        script.content = ['what the hell']
        assert script == ['what the hell']

    def test_21(self):
        script = Script()
        script.append('test line')
        content = ['what the hell']
        script.content = content
        assert script == ['what the hell']
        assert script is not content


class TestScriptRead(object):
    def test_read_1(self):
        fh = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py')
        fh.write('#!/usr/bin/env python\nprint("PyJob is cool!")\n')
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang == '#!/usr/bin/env python'
        assert script.content == ['print("PyJob is cool!")']
        pytest.helpers.unlink([fh.name])

    def test_read_2(self):
        fh = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py')
        fh.write('print("PyJob is cool!")\n')
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang == ''
        assert script.content == ['print("PyJob is cool!")']
        pytest.helpers.unlink([fh.name])

    def test_read_3(self):
        fh = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix=ScriptProperty.SHELL.suffix)
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang == ''
        assert script.content == []
        pytest.helpers.unlink([fh.name])

    def test_read_4(self):
        fh = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix=ScriptProperty.SHELL.suffix)
        fh.write(ScriptProperty.SHELL.shebang)
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang == ScriptProperty.SHELL.shebang
        assert script.content == []
        pytest.helpers.unlink([fh.name])

    @pytest.mark.skipif(pytest.on_windows, reason='Unavailable on Windows')
    def test_read_5(self):
        fh = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix=ScriptProperty.SHELL.suffix)
        fh.write('\n' + ScriptProperty.SHELL.shebang)
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang == ''
        assert script.content == ['', ScriptProperty.SHELL.shebang]
        pytest.helpers.unlink([fh.name])

    def test_read_6(self):
        fh = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix=ScriptProperty.SHELL.suffix)
        fh.write('\n' + '')
        fh.close()
        script = Script.read(fh.name)
        assert script.shebang == ''
        assert script.content == ['']
        pytest.helpers.unlink([fh.name])

    @pytest.mark.skipif(pytest.on_windows, reason='Unavailable on Windows')
    def test_read_7(self):
        fh = tempfile.NamedTemporaryFile(
            mode='w',
            dir='.',
            delete=True,
            prefix='pyjob',
            suffix=ScriptProperty.SHELL.suffix)
        script = Script.read(fh.name)
        fh.close()
        assert script.directory == os.getcwd()
        assert script.prefix == ''
        assert script.stem[:5] == 'pyjob'
        assert script.suffix == ScriptProperty.SHELL.suffix


class TestIsValidScriptPath(object):
    def test_is_valid_script_path_1(self):
        fh = tempfile.NamedTemporaryFile(delete=True)
        fh.close()
        assert not is_valid_script_path(fh.name)

    @pytest.mark.skipif(pytest.on_windows, reason='Unavailable on Windows')
    def test_is_valid_script_path_2(self):
        fh = tempfile.NamedTemporaryFile(delete=True)
        assert not is_valid_script_path(fh.name)
        fh.close()

    def test_is_valid_script_path_3(self):
        fh = tempfile.NamedTemporaryFile(delete=True)
        os.chmod(fh.name, 0o777)
        assert is_valid_script_path(fh.name)
        fh.close()


class TestScriptProperty(object):
    def test_1(self):
        if pytest.on_windows:
            assert ScriptProperty.PERL.shebang == ''
        else:
            assert ScriptProperty.PERL.shebang == '#!/usr/bin/env perl'
        assert ScriptProperty.PERL.suffix == '.pl'

    def test_2(self):
        if pytest.on_windows:
            assert ScriptProperty.PYTHON.shebang == ''
        else:
            assert ScriptProperty.PYTHON.shebang == '#!/usr/bin/env python'
        assert ScriptProperty.PYTHON.suffix == '.py'

    def test_3(self):
        if pytest.on_windows:
            assert ScriptProperty.SHELL.shebang == ''
            assert ScriptProperty.SHELL.suffix == '.bat'
        else:
            assert ScriptProperty.SHELL.shebang == '#!/bin/bash'
            assert ScriptProperty.SHELL.suffix == '.sh'


class TestLocalScriptCreator(object):
    def __call__(self, option):
        return self.example_function(option)

    def example_function(self, option):
        cmd = ['echo {}'.format(option)]
        script = Script(directory=os.getcwd())
        for c in cmd:
            script.append(c)
        return script

    def test_1(self):
        nproc = 2
        options = [1, 2, 3, 4, 5]
        script_creator = LocalScriptCreator(func=self, iterable=options, processes=nproc)
        collector = script_creator.collector()
        assert collector.scripts == [['echo 1'],
                                     ['echo 2'],
                                     ['echo 3'],
                                     ['echo 4'],
                                     ['echo 5']]
