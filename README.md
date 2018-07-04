
# PyJob

**Python-controlled job execution across multiple platforms**

[![PyPi package](https://img.shields.io/pypi/v/pyjob.svg)](https://pypi.python.org/pypi/pyjob)
[![Build Status](https://travis-ci.org/fsimkovic/pyjob.svg)](https://travis-ci.org/fsimkovic/pyjob)
[![Python version](https://img.shields.io/pypi/pyversions/pyjob.svg)](https://pypi.python.org/pypi/pyjob)

## Installation

### Latest official release
```bash
$ pip install pyjob
```

### Source code
```bash
$ git clone https://github.com/fsimkovic/pyjob.git
$ cd pyjob
$ python setup install
```

## Examples

### Launch independent processes executing one or more script across multiple platforms 

#### Single script

```python
>>> from pyjob import Queue
>>> with Queue('local') as queue:
...     queue.submit('run.sh', nproc=1)
...     queue.wait()
```

The first argument added to the constructor call --- `local` in the above example --- defines the platform.
Different platforms are available, and their commonly used abbreviations can be used. 

| Platform                | Argument | 
| ----------------------- | -------- |
| Local Machine           | `local`  |
| Sun Grid Engine         | `sge`    |
| Load Sharing Facility   | `lsf`    |
| Portable Batch System   | `pbs`    |
| TORQUE Resource Manager | `torque` |

#### Multiple scripts

```python
>>> from pyjob import Queue
>>> queue = Queue('sge')
>>> queue.submit(['run_1.sh', 'run_2.sh'])
```

### Create a pool to spread execution across one or more threads

```python
>>> from pyjob import Pool
>>> with Pool(processes=4) as pool:
...     pool.map(f, args)
```

The implementation of `pyjob.Pool` creates a context for `multiprocessing.Pool` to allow easier termination
of threads and catch exceptions.
