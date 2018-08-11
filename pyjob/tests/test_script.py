__author__ = 'Felix Simkovic'

import os
import pytest
import tempfile

from pyjob.script import Script, is_valid_script_path


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
