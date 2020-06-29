import logging
import os
import sys
from collections import UserDict
from functools import wraps

import yaml
from pyjob.exception import DictLockedError

logger = logging.getLogger(__name__)


class ImmutableDictMixin(object):
    _locked = False

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    @staticmethod
    def assert_lock(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            if self._locked:
                raise DictLockedError("Dictionary locked, cannot override value")
            return fn(self, *args, **kwargs)

        return wrapper


class PyJobConfig(UserDict, ImmutableDictMixin):

    _directory = os.path.expanduser("~/.pyjob")
    if not os.path.isdir(_directory):
        try:
            os.makedirs(_directory)
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(_directory):
                pass
            else:
                raise RuntimeError("Cannot create configuration directory")

    file = os.path.join(_directory, "pyjob.yml")
    if not os.path.isfile(file):
        open(file, "w").close()

    @ImmutableDictMixin.assert_lock
    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    @ImmutableDictMixin.assert_lock
    def setdefault(self, key, value=None):
        super().setdefault(key, value=value)
        self.write()

    @ImmutableDictMixin.assert_lock
    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

    def write(self):
        data = yaml.dump(dict(self), default_flow_style=False)
        with open(self.file, "w") as f:
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
            raise FileNotFoundError("Cannot find YAML file")
        with open(yamlf, "r") as f:
            data = yaml.safe_load(f)
        data = data or {}
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
