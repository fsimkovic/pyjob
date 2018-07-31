**[unreleased]**

**[0.2]**

*Added*

- Extended total number of independent jobs allowed on local server
- :obj:`~pyjob.pool.Pool` contextmanager added to allow proper clear-up ... built around :obj:`multiprocessing.Pool`

*Changed*

- :obj:`~pyjob.job.Job` renamed to `~pyjob.queue.Queue` although backwards compatible
- :obj:`~pyjob.queue.Queue` can be used as context

**[0.1.5]**

*Added*

- `MANIFEST.in` file added - thanks @mobiusklein

**[0.1.4]**

*Added*

- Support for PBS/TORQUE added [experimental]

*Changed*

- Renamed :func:`~pyjob.platform.platform_factory` to :func:`~pyjob.platform.Platform()`
- Renamed :const:`~pyjob.platform.platform.Platform.TASK_ID` to :const:`~pyjob.platform.platform.Platform.ARRAY_TASK_ID`

*Fixed*

- :obj:`~pyjob.platform.worker.Worker` terminates properly

**[0.1.3]**

*Changed*

- Critical bug fix in :func:`~pyjob.platform.prep_array_script` for cluster job submission

**[0.1.2]**

*Changed*

- :exc:`~pyjob.exception.PyJobNotImplementedError` replaced with :exc:`NotImplementedError`
- Bug fix for script submission in :meth:`~pyjob.job.Job.submit`

**[0.1.1]**

*Changed*

- Fix for PyPi installation
- Added additional information to `README.rst` file

**[0.1]**

*Added*

- Initial release
