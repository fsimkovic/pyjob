"""Job Management Controller"""

__author__ = "Felix Simkovic"
__version__ = "1.0"

from distutils.util import convert_path
from setuptools import setup

import os

# ==============================================================
# Functions, functions, functions ... 
# ==============================================================


def readme():
    with open('README.rst', 'r') as f_in:
        return f_in.read()


def version():
    """Get the current PyJob version"""
    # Credits to http://stackoverflow.com/a/24517154
    main_ns = {}
    ver_path = convert_path(os.path.join('pyjob', 'version.py'))
    with open(ver_path) as f_in:
        exec(f_in.read(), main_ns)
    return main_ns['__version__']


# ==============================================================
# Define all the relevant options
# ==============================================================
AUTHOR = "Felix Simkovic"
AUTHOR_EMAIL = "felixsimkovic@me.com"
DESCRIPTION = __doc__.replace("\n", "")
LICENSE = "MIT License"
LONG_DESCRIPTION = readme()
PACKAGE_DIR = "pyjob"
PACKAGE_NAME = "pyjob"
URL = "https://github.com/fsimkovic/pyjob"
VERSION = version()

PACKAGES = [
    'pyjob',
    'pyjob/misc',
    'pyjob/platform',
]

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
]

# Do the actual setup below
setup(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    name=PACKAGE_NAME,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    version=VERSION,
    url=URL,
    packages=PACKAGES,
    package_dir={PACKAGE_NAME: PACKAGE_DIR},
    classifiers=CLASSIFIERS,
    test_suite='nose.collector',
    tests_require=['nose >=1.3.7'],
    zip_safe=False,
)
