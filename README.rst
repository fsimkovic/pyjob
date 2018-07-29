*****
PyJob
*****

**Python-controlled job execution across multiple platforms**

.. image:: https://img.shields.io/pypi/v/pyjob.svg
   :target: https://pypi.python.org/pypi/pyjob
   :alt: PyPi package

.. image:: https://travis-ci.org/fsimkovic/pyjob.svg
   :target: https://travis-ci.org/fsimkovic/pyjob
   :alt: Build Status

.. image:: https://img.shields.io/pypi/pyversions/pyjob.svg
   :target: https://pypi.python.org/pypi/pyjob
   :alt: Python version

Installation
++++++++++++

**Latest official release**

.. code-block:: bash
   
   $ pip install pyjob

**Source code**

.. code-block:: bash
   
   $ git clone https://github.com/fsimkovic/pyjob.git
   $ cd pyjob
   $ python setup install

Quickstart
++++++++++

** Single script**

.. code-block:: python

   >>> from pyjob import QueueFactory
   >>> with QueueFactory('local', processes=1) as queue:
   ...     queue.submit('run.sh')

The first argument added to the constructor call --- `local` in the above example --- defines the platform.
Different platforms are available, and their commonly used abbreviations can be used. 

+-------------------------+----------+
| Platform                | Argument | 
+=========================+==========+
| Local Machine           | `local`  |
+-------------------------+----------+
| Sun Grid Engine         | `sge`    |
+-------------------------+----------+
.. | Load Sharing Facility   | `lsf`    |
.. +-------------------------+----------+
.. | Portable Batch System   | `pbs`    |
.. +-------------------------+----------+
.. | TORQUE Resource Manager | `torque` |
.. +-------------------------+----------+

**Multiple scripts**

.. code-block:: python

   >>> from pyjob import QueueFactory
   >>> with QueueFactory('sge') as queue:
   ...     queue.submit(['run_1.sh', 'run_2.sh'])


**Function calls in Python**

.. code-block:: python

   >>> from pyjob import Pool
   >>> with Pool(processes=4) as pool:
   ...     pool.map(f, args)

The implementation of :obj:`Pool <pyjob.pool.Pool>` creates a context for :obj:`multiprocessing.Pool` to allow easier termination of threads and catch exceptions.
