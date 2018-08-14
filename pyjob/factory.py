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

import importlib
import logging

from pyjob.exception import PyJobUnknownTaskPlatform

TASK_PLATFORMS = {
    'local': ('pyjob.local', 'LocalTask'),
    'lsf': ('pyjob.lsf', 'LoadSharingFacilityTask'),
    'pbs': ('pyjob.pbs', 'PortableBatchSystemTask'),
    'slurm': ('pyjob.slurm', 'SlurmTask'),
    'sge': ('pyjob.sge', 'SunGridEngineTask'),
    'torque': ('pyjob.torque', 'TorqueTask'),
}

logger = logging.getLogger(__name__)


def TaskFactory(platform, *args, **kwargs):
    """Accessibility function for any :obj:`~pyjob.task.Task`

    Examples
    --------

    >>> from pyjob import TaskFactory
    >>> with TaskFactory('local', script) as task:
    ...     task.run()

    Parameters
    ----------
    platform : str
       The platform to create the :obj:`~pyjob.task.Task` on
    *args : tuple
       Any positional arguments relevant to the :obj:`~pyjob.task.Task`
    **kwargs : dict
       Any keyword arguments relevant to the :obj:`~pyjob.task.Task`

    Raises
    ------
    :exc:`~pyjob.exception.PyJobUnknownTaskPlatform`
       Unknown platform

    """
    platform = platform.lower()
    if platform in TASK_PLATFORMS:
        logger.debug('Found requested platform in available task list')
        module, class_ = TASK_PLATFORMS[platform]
        return getattr(importlib.import_module(module), class_)(*args, **kwargs)
    else:
        raise PyJobUnknownTaskPlatform('Unknown platform: %s' % platform)
