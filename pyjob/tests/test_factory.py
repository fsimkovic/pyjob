__author__ = 'Felix Simkovic'

import importlib
import os
import pytest

from pyjob.exception import PyJobUnknownTaskPlatform
from pyjob.factory import TaskFactory, TASK_PLATFORMS


class TestFactory(object):
    def test_1(self):
        task = TaskFactory(TASK_PLATFORMS.keys()[0], None)
        assert task.script == []

    def test_2(self):
        task = TaskFactory(TASK_PLATFORMS.keys()[0].upper(), None)
        assert task.script == []

    def test_3(self):
        task = pytest.helpers.randomstr()
        while task in TASK_PLATFORMS:
            task = pytest.helpers.randomstr()
        with pytest.raises(PyJobUnknownTaskPlatform):
            TaskFactory(task, None)

    def test_4(self):
        for _, v in TASK_PLATFORMS.items():
            module, class_ = v
            assert getattr(importlib.import_module(module), class_)
