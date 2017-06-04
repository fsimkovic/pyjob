"""PyJob library for Python-controlled job execution across multiple platforms"""

__author__ = "Felix Simkovic"
__email__ = "felixsimkovic@me.com"

from pyjob import version
__version__ = version.__version__


def Job(*args, **kwargs):
    from pyjob.dispatch import Job
    return Job(*args, **kwargs)
