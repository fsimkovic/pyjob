.. _quickstart:

Quickstart
----------

Script creation
~~~~~~~~~~~~~~~

A :obj:`~pyjob.script.Script` is easily created by simply providing some optional information. Content can be stored just like any other Python :obj:`list`. 

.. code-block:: python
   
   >>> from pyjob import Script
   >>> script = Script(directory='.', prefix='example', stem='', suffix='.sh')
   >>> script.append('sleep 5')
   >>> print(script)
   #!/bin/bash
   sleep 5

The path to the :obj:`~pyjob.script.Script` can be retrieved by accessing the associated :attr:`~pyjob.script.Script.path` attribute.

.. code-block:: python

   >>> print(script.path)
   './example.sh'

We could also :meth:`~pyjob.script.Script.write` the :obj:`~pyjob.script.Script` to disk, but do not worry, the :obj:`~pyjob.task.Task` would do this for you in case you forget before execution.

.. code-block:: python

   >>> script.write()

If we are provided with a script written to disk, i.e. reverse the previous few steps, we could simply use the :meth:`read_script <pyjob.script.Script.read>` function, and obtain a :obj:`~pyjob.script.Script` instance. This would also allow us to conveniently edit a :obj:`~pyjob.script.Script` if necessary.

.. code-block:: python

   >>> from pyjob import read_script
   >>> script = read_script('./example.sh')
   >>> print(script)
   #!/bin/bash
   sleep 5

To create multiple scripts in parallel we can use the :obj:`LocalScriptCreator <pyjob.script.LocalScriptCreator>`, given a function to generate a single :obj:`~pyjob.script.Script`, an iterable containing the options for each script, and the number of processors to use. You can access the :attr:`collector <pyjob.script.LocalScriptCreator.collector>`, which will return the :obj:`~pyjob.script.ScriptCollector` that can then be input directly into :obj:`TaskFactory <pyjob.factory.TaskFactory>` for execution (detailed below).


.. code-block:: python

   >>> from pyjob.script import LocalScriptCreator
   >>> script_creator = LocalScriptCreator(func=example_function, iterable=example_iterable, processes=2)
   >>> collector = script_creator.collector()

Execution of single script on a local machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :obj:`~pyjob.script.Script` created in the previous step can be easily executed across all supported platforms, i.e. operating systems and HPC queueing systems. To do so, we simply select a platform (`local` in the example below), provide one or more :obj:`~pyjob.script.Script` instances or paths to scripts, and then execute with the :meth:`~pyjob.task.Task.run` method. To simplify the selection of the correct platform, a :obj:`~pyjob.factory.TaskFactory` is provided.

.. code-block:: python

   >>> from pyjob import TaskFactory
   >>> with TaskFactory('local', script) as task:
   ...     task.run()

In the example, the :obj:`~pyjob.task.Task` is handled with a Python context, which is the recommended way to handle all :obj:`~pyjob.task.Task` instances.

Execution of multiple scripts on a local machine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> def dup_script(s, i=0):
   ...     s1 = s[:]
   ...     s1.stem = str(i)
   ...     return s1
   >>> script1 = dup_script(script, i=0)
   >>> script2 = dup_script(script, i=1)
   
This process is identical to the previous example, except that this time we provide the :obj:`~pyjob.script.Script` instances as :obj:`list`.

.. code-block:: python

   >>> with TaskFactory('local', [script1, script2]) as task:
   ...     task.run()

If we would like to use multiple processes, simply provide the `processes` keyword argument with the relevant count.

.. code-block:: python

   >>> with TaskFactory('local', [script1, script2], processes=2) as task:
   ...     task.run()

If a list of :obj:`~pyjob.script.Script` instances is inconvenient to maintain, or you would like to use the latest implementation, you could also use the :obj:`~pyjob.script.ScriptCollector` and provide it instead.

.. code-block:: python

   >>> from pyjob.script import ScriptCollector
   >>> collector = ScriptCollector(script)
   >>> for i in range(5):
   ...     script = dup_script(script, i=i)
   ...     collector.add(script)
   >>> with TaskFactory('local', collector, processes=2) as task:
   ...     task.run()

Execution of multiple scripts on non-local platforms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> with TaskFactory('sge', [script1, script2]) as task:
   ...     task.run()

The first argument to :obj:`~pyjob.factory.TaskFactory`, ``sge`` in this example, defines the 
platform on which the :obj:`~pyjob.task.Task` will be executed. Other options exist and you 
can try this by installing PyJob on such a machine and substituting any of below options in.

.. rst-class:: table-hover

+-------------------------+------------+-------------------------------------------+
| Platform                | Argument   | Task class                                |
+=========================+============+===========================================+
| Local Machine           | ``local``  | :obj:`~pyjob.local.LocalTask`             |
+-------------------------+------------+-------------------------------------------+
| Sun Grid Engine         | ``sge``    | :obj:`~pyjob.sge.SunGridEngineTask`       |
+-------------------------+------------+-------------------------------------------+
| Slurm                   | ``slurm``  | :obj:`~pyjob.slurm.SlurmTask`             |
+-------------------------+------------+-------------------------------------------+
| Load Sharing Facility   | ``lsf``    | :obj:`~pyjob.lsf.LoadSharingFacilityTask` |
+-------------------------+------------+-------------------------------------------+
| Portable Batch System   | ``pbs``    | :obj:`~pyjob.pbs.PortableBatchSystemTas`  |
+-------------------------+------------+-------------------------------------------+
| TORQUE Resource Manager | ``torque`` | :obj:`~pyjob.torque.TorqueTask`           |
+-------------------------+------------+-------------------------------------------+

Execution of Python functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This little nugget is simply an extension to :obj:`multiprocessing.Pool` to simplify and tidy imports in your own code. It also provides a backwards-compatible context for the :obj:`multiprocessing.Pool`, which is standard in Python3.

.. code-block:: python
   
   >>> import time
   >>> def sleep(t):
   ...     time.sleep(t)

.. code-block:: python
  
   >>> from pyjob import Pool
   >>> with Pool(processes=4) as pool:
   ...     pool.map(sleep, [10] * 8)
