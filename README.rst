
*****
PyJob
*****

**Python-controlled job execution across multiple platforms**

.. image:: https://img.shields.io/pypi/v/pyjob.svg
   :target: https://pypi.python.org/pypi/pyjob
   :alt: PyPi Package

.. image:: https://img.shields.io/pypi/pyversions/pyjob.svg
   :target: https://pypi.python.org/pypi/pyjob
   :alt: Python Versions

.. image:: https://travis-ci.org/fsimkovic/pyjob.svg?branch=master
   :target: https://travis-ci.org/fsimkovic/pyjob
   :alt: Travis Build


Installation
++++++++++++

.. code-block:: bash

   $> git clone https://github.com/fsimkovic/pyjob.git
   $> cd pyjob
   $> python setup install


Examples
++++++++

1. To run a script called 'run.sh' on a local machine

.. code-block:: python 

   >>> from pyjob import Job
   >>> j = Job('local')
   >>> j.submit('run.sh', nproc=1)
   >>> j.wait()


2. To run a script called 'run.sh' on a SGE management platform

.. code-block:: python
   
   >>> from pyjob import Job 
   >>> j = Job('sge')
   >>> j.submit('run.sh')
   >>> j.wait()


3. To run a script called 'run.sh' on a LSF management platform

.. code-block:: python

   >>> from pyjob import Job 
   >>> j = Job('lsf')
   >>> j.submit('run.sh')
   >>> j.wait()
