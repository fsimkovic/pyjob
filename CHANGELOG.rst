**[unreleased]**

- Allow :obj:`~multiprocessing.Pool` processes to be set by default configuration file

**[0.3.0]**

- [`#15 <https://github.com/fsimkovic/pyjob/issues/15>`_] - configuration file added to control user-specific default settings

**[0.2.1]**

*Changed*

- Backend to generate array scripts generalised

**[0.2]**

*Added*

- [`#22 <https://github.com/fsimkovic/pyjob/issues/22>`_] - :obj:`~pyjob.script.LocalScriptCreator` added to simplify multi-core :obj:`~pyjob.script.Script` generation
- :obj:`~pyjob.task.Task` backend for script collection modified to store everything in :obj:`~pyjob.script.Script` instances collected in a :obj:`~pyjob.script.ScriptCollector` instance
- :obj:`~pyjob.script.ScriptCollector` added to support easier collection of multiple :obj:`~pyjob.script.Script` instances
- [`#14 <https://github.com/fsimkovic/pyjob/issues/14>`_] - :obj:`~pyjob.slurm.SlurmTask` support added
- [`#13 <https://github.com/fsimkovic/pyjob/issues/13>`_] - :func:`~pyjob.cexec.cexec` accepts all :obj:`~subprocess.Popen` keyword arguments
- [`#12 <https://github.com/fsimkovic/pyjob/issues/12>`_] - `pyjob` command-line executable to provide conveniont script submission without active Python interpreter
- [`#11 <https://github.com/fsimkovic/pyjob/issues/11>`_] - Contextmanager support for :obj:`~pyjob.stopwatch.StopWatch` instances 
- [`#10 <https://github.com/fsimkovic/pyjob/issues/10>`_] - Contextmanager support for all :obj:`~pyjob.task.Task` instances
- [`#9 <https://github.com/fsimkovic/pyjob/issues/9>`_] - Codecov support added
- [`#8 <https://github.com/fsimkovic/pyjob/issues/8>`_] - Sphinx documentation added [hosted on ReadTheDocs.org]
- [`#3 <https://github.com/fsimkovic/pyjob/issues/3>`_] - :obj:`~pyjob.script.Script` interface to read/write scripts conveniently
- Convenience function :meth:`~pyjob.misc.deprecate` for faster/more readable deprecation tagging
- Better execution handling of all cluster platforms wrt running directory

*Changed*

- Backend architecture refactored. Previous :obj:`~pyjob.job.Job` class merged with :obj:`~pyjob.platform.platform.Platform` class to become abstract base class :obj:`~pyjob.task.Task`. Backwards-compatibility maintained but is going to be deprecated with release 0.3

*Fixed*

- [`#19 <https://github.com/fsimkovic/pyjob/issues/19>`_] - :meth:`pyjob.local.LocalTask.wait` did not function behave correctly when STDOUT was piped to separate log
- [`#18 <https://github.com/fsimkovic/pyjob/issues/18>`_] - Better handling of incomplete executable paths
- [`#6 <https://github.com/fsimkovic/pyjob/issues/6>`_] - Bug fix in :func:`pyjob.cexec.cexec` to enable decoding of other :obj:`bytes` encodings than ASCII, which may be returned by :meth:`subprocess.Popen.communicate`
- Bug fix in :obj:`~pyjob.local.LocalTask` to prevent deadlock when processes did not terminate properly
- Bug fix in :meth:`pyjob.task.Task.wait` that attempted to call a :obj:`bool` in rare occasions

*Removed*

- :mod:`pyjob.misc` and :mod:`pyjob.platform` deprecated in favour of (temporary) modules
