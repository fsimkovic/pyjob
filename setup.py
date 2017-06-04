"""Sequence Independent Molecular Replacement Based on Available Database"""

__author__ = "Felix Simkovic"
__version__ = "1.0"

from distutils.command.build import build
from distutils.util import convert_path
from setuptools import setup

import os
import shutil
import sys

# ==============================================================
# Functions, functions, functions ... 
# ==============================================================


def readme():
    with open('README.md', 'r') as f_in:
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
# Determine the Python executable
# ==============================================================
PYTHON_EXE = None
for arg in sys.argv:
    if arg[0:20] == "--script-python-path" and len(arg) == 20:
        option, value = arg, sys.argv[sys.argv.index(arg) + 1]
        PYTHON_EXE = value
    elif arg[0:20] == "--script-python-path" and arg[20] == "=":
        option, value = arg[:20], arg[21:]
        PYTHON_EXE = value

if not PYTHON_EXE:
    PYTHON_EXE = sys.executable

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
URL = "https://github.com/rigdenlab/SIMBAD"
VERSION = version()

PACKAGES = [
    'pyjob',
    'pyjob/dispatch',
    'pyjob/misc',
    'pyjob/platform',
]

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
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
    include_package_data=True,
    zip_safe=False,
)
