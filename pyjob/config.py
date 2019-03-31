# MIT License
#
# Copyright (c) 2017-18 Felix Simkovic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'Felix Simkovic'
__version__ = '1.0'

import logging
import os
import sys
import yaml

from pyjob.exception import PyJobConfigLockedException

if sys.version_info.major < 3:
    FileNotFoundError = IOError
    from UserDict import UserDict
else:
    from collections import UserDict

logger = logging.getLogger(__name__)


class PyJobConfig(UserDict):

    _locked = False
    _directory = os.path.expanduser('~/.pyjob')
    if not os.path.isdir(_directory):
        try:
            os.makedirs(_directory)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(_directory):
                pass
            else:
                raise RuntimeError('Cannot create configuration directory')
    file = os.path.join(_directory, 'pyjob.yml')
    if not os.path.isfile(file):
        open(file, 'w').close()

    def __setitem__(self, key, value):
        if self._locked:
            raise PyJobConfigLockedException('Dictionary locked, cannot override value')
        super(PyJobConfig, self).__setitem__(key, value)

    def setdefault(self, key, value=None):
        if self._locked:
            raise PyJobConfigLockedException('Dictionary locked, cannot override value')
        super(PyJobConfig, self).setdefault(key, value=value)
        self.write()

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def update(self, *args, **kwargs):
        if self._locked:
            raise PyJobConfigLockedException('Dictionary locked, cannot override value')
        super(PyJobConfig, self).update(*args, **kwargs)

    def write(self):
        data = yaml.dump(dict(self), default_flow_style=False)
        with open(self.file, 'w') as f:
            f.write(data)

    @staticmethod
    def read_yaml(yamlf):
        """Read a YAML file

        Parameters
        ----------
        yamlf : str
           The path to a PyJob YAML config file

        Returns
        -------
        :obj:`~pyjob.config.PyJobConfig`
           A :obj:`~pyjob.config.PyJobConfig` instance

        Raises
        ------
        :exc:`FileNotFoundError`
           Cannot find YAML file

        """
        if not os.path.isfile(yamlf):
            raise FileNotFoundError('Cannot find YAML file')
        with open(yamlf, 'r') as f:
            data = yaml.safe_load(f)
        if data is None:
            data = {}
        config = PyJobConfig(**data)
        config.dir = os.path.dirname(yamlf)
        config.file = yamlf
        return config

    @classmethod
    def from_default(cls):
        """Construct the configuration from the default file

        Returns
        -------
        :obj:`~pyjob.config.PyJobConfig`
           A :obj:`~pyjob.config.PyJobConfig` instance

        """
        return PyJobConfig.read_yaml(cls.file)
