.. _quickstart:

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

**Execution of multiple scripts on non-local platforms**

.. code-block:: python

   >>> with TaskFactory('sge', [script1.path, script2.path]) as task:
   ...     task.run()

The first argument to :obj:`~pyjob.factory.TaskFactory`, `sge` in this example, defines the 
platform on which the :obj:`~pyjob.task.Task` will be executed. Other options exist and you 
can try this by installing PyJob on such a machine and substituting any of below commands in.

.. rst-class:: table-hover

+-------------------------+----------+-------------------------------------------+
| Platform                | Argument | Task class                                |
+=========================+==========+===========================================+
| Local Machine           | `local`  | :obj:`~pyjob.local.LocalTask`             |
+-------------------------+----------+-------------------------------------------+
| Sun Grid Engine         | `sge`    | :obj:`~pyjob.sge.SunGridEngineTask`       |
+-------------------------+----------+-------------------------------------------+
| Load Sharing Facility   | `lsf`    | :obj:`~pyjob.lsf.LoadSharingFacilityTask` |
+-------------------------+----------+-------------------------------------------+
| Portable Batch System   | `pbs`    | :obj:`~pyjob.pbs.PortableBatchSystemTas`  |
+-------------------------+----------+-------------------------------------------+
| TORQUE Resource Manager | `torque` | :obj:`~pyjob.torque.TorqueTask`           |
+-------------------------+----------+-------------------------------------------+

**Execution of Python functions**

.. code-block:: python
   
   >>> import time
   >>> def sleep(t):
   ...     time.sleep(t)

.. code-block:: python
  
   >>> from pyjob import Pool
   >>> with Pool(processes=4) as pool:
   ...     pool.map(sleep, [10] * 8)
