class DictLockedError(Exception):
    pass


class PyJobError(Exception):
    pass


class PyJobExecutionError(PyJobError):
    pass


class PyJobExecutableNotFoundError(PyJobError):
    pass


class PyJobTaskLockedError(PyJobError):
    pass


class PyJobUnknownTaskPlatform(PyJobError):
    pass
