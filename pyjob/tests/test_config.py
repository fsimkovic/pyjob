__author__ = 'Felix Simkovic'

import os
import pytest
import sys

from pyjob.config import PyJobConfig
from pyjob.exception import PyJobConfigLockedException

if sys.version_info.major < 3:
    FileNotFoundError = IOError


class TestPyJobConfig(object):
    def test_1(self):
        config = PyJobConfig()
        assert config == {}

    def test_2(self):
        config = PyJobConfig(platform='local', processes=2)
        assert config == {'platform': 'local', 'processes': 2}

    def test_3(self):
        config = PyJobConfig(platform='local', processes=2)
        assert config == {'platform': 'local', 'processes': 2}
        config['platform'] = 'sge'
        assert config == {'platform': 'sge', 'processes': 2}

    def test_4(self):
        parameters = {'platform': 'local', 'processes': 2}
        config = PyJobConfig(**parameters)
        assert config == parameters


class TestPyJobConfigWrite(object):
    def test_1(self):
        config_w = PyJobConfig(platform='local', processes=2)
        config_w.file = 'test_config.yaml'
        config_w.write()
        config_r = PyJobConfig.read_yaml(config_w.file)
        assert config_r == config_w
        os.unlink(config_w.file)


class TestPyJobConfigRead(object):
    @staticmethod
    def get_config_file(fname='test_config.yaml'):
        template = """platform: local
processes: 1
debug: False
cutoff: 1.0
"""
        with open(fname, 'w') as f:
            f.write(template)
        return fname

    def test_1(self):
        fname = TestPyJobConfigRead.get_config_file()
        config = PyJobConfig.read_yaml(fname)
        assert config['platform'] == 'local'
        assert config['processes'] == 1
        assert not config['debug']
        assert config['cutoff'] == 1.0
        os.unlink(fname)

    def test_2(self):
        with pytest.raises(FileNotFoundError):
            PyJobConfig.read_yaml('foobar.yaml')

    def test_3(self):
        fname = TestPyJobConfigRead.get_config_file()
        config = PyJobConfig.read_yaml(fname)
        assert config['platform'] == 'local'
        config['platform'] = 'sge'
        assert config['platform'] == 'sge'
        config.lock()
        with pytest.raises(PyJobConfigLockedException):
            config['platform'] = 'local'
        config.unlock()
        config['platform'] = 'local'
        assert config['platform'] == 'local'
        os.unlink(fname)
