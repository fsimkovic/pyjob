import importlib
import os
import pytest
from unittest import mock

from pyjob.exception import PyJobUnknownTaskPlatform
from pyjob.factory import TaskFactory, TASK_PLATFORMS


@mock.patch("pyjob.lsf.LoadSharingFacilityTask._check_requirements")
@mock.patch("pyjob.pbs.PortableBatchSystemTask._check_requirements")
@mock.patch("pyjob.slurm.SlurmTask._check_requirements")
@mock.patch("pyjob.sge.SunGridEngineTask._check_requirements")
@mock.patch("pyjob.torque.TorqueTask._check_requirements")
class TestFactory(object):
    def test_1(self, *args):
        for mock_func in args:
            mock_func.return_value = None
        task = TaskFactory(next(iter(TASK_PLATFORMS)), None)
        assert task.script == []

    def test_2(self, *args):
        for mock_func in args:
            mock_func.return_value = None
        task = TaskFactory(next(iter(TASK_PLATFORMS)).upper(), None)
        assert task.script == []

    def test_3(self, *args):
        task = pytest.helpers.randomstr()
        while task in TASK_PLATFORMS:
            task = pytest.helpers.randomstr()
        with pytest.raises(PyJobUnknownTaskPlatform):
            TaskFactory(task, None)

    def test_4(self, *args):
        for _, v in TASK_PLATFORMS.items():
            module, class_ = v
            assert getattr(importlib.import_module(module), class_)
