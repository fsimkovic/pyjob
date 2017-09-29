
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

### Local machine

```python
>>> from pyjob import Job
>>> j = Job('local')
>>> j.submit('run.sh', nproc=1)
>>> j.wait()
```

### SGE management platform

```python 
>>> from pyjob import Job 
>>> j = Job('sge')
>>> j.submit('run.sh')
>>> j.wait()
```

### LSF management platform

```python
>>> from pyjob import Job 
>>> j = Job('lsf')
>>> j.submit('run.sh')
>>> j.wait()
```

### PBS/TORQUE management platform

```python
>>> from pyjob import Job 
>>> j = Job('pbs')
>>> j.submit('run.sh')
>>> j.wait()
```
