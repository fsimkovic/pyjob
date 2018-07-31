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

**Script creation**

.. code-block:: python
   
   >>> from pyjob import Script
   >>> script = Script(directory='.', prefix='example', stem='', suffix='.sh')
   >>> script.append('sleep 5')
   >>> print(script)
   #!/bin/bash
   sleep 5
   >>> print(script.path)
   './example.sh'
   >>> script.write()

**Execution of single script on local machine**

.. code-block:: python

   >>> from pyjob import TaskFactory
   >>> with TaskFactory('local', script.path) as task:
   ...     task.run()

**Execution of multiple scripts on local machine**

.. code-block:: python

   >>> def dup_script(s, i=0):
   ...     s1 = s[:]
   ...     s1.stem = str(i)
   ...     sq.write()
   ...     return s1
   >>> script1 = dup_script(script, i=0)
   >>> script2 = dup_script(script, i=1)
   
.. code-block:: python

   >>> with TaskFactory('local', [script1.path, script2.path]) as task:
   ...     task.run()

.. code-block:: python

   >>> with TaskFactory('local', [script1.path, script2.path], processes=2) as task:
   ...     task.run()

**Execution of multiple scripts on SunGridEngine**

.. code-block:: python

   >>> with TaskFactory('sge', [script1.path, script2.path]) as task:
   ...     task.run()


**Execution of Python functions**

.. code-block:: python
   
   >>> import time
   >>> def sleep(t):
   ...     time.sleep(t)

.. code-block:: python
  
   >>> from pyjob import Pool
   >>> with Pool(processes=4) as pool:
   ...     pool.map(sleep, [10] * 8)
   
