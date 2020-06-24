import importlib
import logging

from pyjob.exception import PyJobUnknownTaskPlatform

TASK_PLATFORMS = {
    "local": ("pyjob.local", "LocalTask"),
    "lsf": ("pyjob.lsf", "LoadSharingFacilityTask"),
    "pbs": ("pyjob.pbs", "PortableBatchSystemTask"),
    "slurm": ("pyjob.slurm", "SlurmTask"),
    "sge": ("pyjob.sge", "SunGridEngineTask"),
    "torque": ("pyjob.torque", "TorqueTask"),
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
        logger.debug("Found requested platform in available task list")
        module, class_ = TASK_PLATFORMS[platform]
        return getattr(importlib.import_module(module), class_)(*args, **kwargs)
    else:
        raise PyJobUnknownTaskPlatform(f"Unknown platform: {platform}")
