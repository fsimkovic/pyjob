import contextlib
import multiprocessing


@contextlib.contextmanager
def Pool(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    try:
        yield pool
    except (RuntimeError, KeyboardInterrupt) as e:
        pool.terminate()
        raise e
    else:
        pool.close()
