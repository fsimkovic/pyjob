"""Job Management Controller"""

__author__ = "Felix Simkovic"
__version__ = "1.0"

from distutils.util import convert_path

import os
import sys

try:
    from setuptools import setup
except ImportError:
    sys.exit("Please install setuptools first!")


def readme():
    with open('README.rst', 'r') as f_in:
        return f_in.read()


def dependencies():
    with open('requirements.txt', 'r') as f_in:
        deps = f_in.read().splitlines()
    return deps


def version():
    """Get the current PyJob version"""
    main_ns = {}
    ver_path = convert_path(os.path.join('pyjob', 'version.py'))
    with open(ver_path) as f_in:
        exec(f_in.read(), main_ns)
    return main_ns['__version__']


AUTHOR = "Felix Simkovic"
AUTHOR_EMAIL = "felixsimkovic@me.com"
DESCRIPTION = __doc__.replace("\n", "")
LICENSE = "MIT License"
LONG_DESCRIPTION = readme()
PACKAGE_DIR = "pyjob"
PACKAGE_NAME = "pyjob"
URL = "https://pyjob.rtfd.io"
VERSION = version()

PACKAGES = [
    'pyjob',
]

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]

ENTRY_POINTS = {'console_scripts': ['pyjob = pyjob.__main__:main']}

setup(
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    name=PACKAGE_NAME,
    description=DESCRIPTION,
    entry_points=ENTRY_POINTS,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,
    version=VERSION,
    url=URL,
    packages=PACKAGES,
    package_dir={PACKAGE_NAME: PACKAGE_DIR},
    classifiers=CLASSIFIERS,
    install_requires=dependencies(),
    setup_requires=['pytest-runner'],
    tests_require=['codecov', 'coverage', 'pytest', 'pytest-cov', 'pytest-pep8', 'pytest-helpers-namespace'],
    zip_safe=False,
)
