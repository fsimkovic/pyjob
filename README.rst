
*****
PyJob
*****

**Python-controlled job execution across multiple platforms**

[![PyPi](https://img.shields.io/pypi/v/conkit.svg)]
[![Python Versions](https://img.shields.io/pypi/pyversions/conkit.svg)]
[![Build Status](https://travis-ci.org/fsimkovic/pyjob.svg?branch=master)](https://travis-ci.org/fsimkovic/pyjob)

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
