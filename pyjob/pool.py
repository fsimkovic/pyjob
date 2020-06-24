import multiprocessing.pool
import sys

from pyjob import config


class Pool(multiprocessing.pool.Pool):
    """:obj:`~multiprocessing.pool.Pool` of processes to allow concurrent method calls

    Examples
    --------

    >>> from pyjob import Pool
    >>> with Pool(processes=2) as pool:
    ...     pool.map(<func>, <iterable>)

    """

    def __init__(self, *args, **kwargs):
        processes = kwargs.pop("processes") or config.get("processes") or None
        super(Pool, self).__init__(processes=processes, *args, **kwargs)
