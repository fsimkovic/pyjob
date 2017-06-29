# MIT License
#
# Copyright (c) 2017 Felix Simkovic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Testing facility for pyjob.platform.lsf"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"

import inspect
import os
import time
import unittest

from pyjob.misc import make_script
from pyjob.platform import prep_array_script
from pyjob.platform.lsf import LoadSharingFacility

# Required for Python2.6 support
def skipUnless(condition):
    if condition:
        return lambda x: x
    else:
        return lambda x: None 


@skipUnless("LSF_BINDIR" in os.environ)
class TestLoadSharingFacility(unittest.TestCase):

    # ================================================================================
    # SINGLE JOB SUBMISSIONS

    def test_hold_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = LoadSharingFacility.sub(jobs, hold=False, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        LoadSharingFacility.hold(jobid)
        LoadSharingFacility.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_kill_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        self.assertTrue(LoadSharingFacility.stat(jobid))
        LoadSharingFacility.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_rls_1(self):
        jobs = [make_script(["touch", "pyjob_rls_test_1"])]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        LoadSharingFacility.rls(jobid)
        start, timeout = time.time(), False
        while LoadSharingFacility.stat(jobid):
            # Don't wait too long, one minute, then fail
            if ((time.time() - start) // 60) >= 1:
                LoadSharingFacility.kill(jobid)
                timeout = True
            time.sleep(10)
        for f in jobs:
            os.unlink(f)
        if timeout:
            self.assertEqual(1, 0, "Timeout")
        else:
            self.assertTrue(os.path.isfile('pyjob_rls_test_1'))
            os.unlink('pyjob_rls_test_1')

    def test_stat_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        data = LoadSharingFacility.stat(jobid)
        self.assertTrue(data)
        self.assertEqual(jobid, int(data['job_number']))
        LoadSharingFacility.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_sub_1(self):
        jobs = [make_script(["sleep 1"])]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        self.assertTrue(LoadSharingFacility.stat(jobid))
        LoadSharingFacility.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_sub_2(self):
        assert "PYJOB_ENV" not in os.environ
        os.environ["PYJOB_ENV"] = "pyjob_random"
        jobs = [make_script(["echo $PYJOB_ENV"], directory=os.getcwd())]
        log = jobs[0].replace(".sh", ".log")
        jobid = LoadSharingFacility.sub(jobs, log=log, directory=os.getcwd(),
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        while LoadSharingFacility.stat(jobid):
            time.sleep(1)
        self.assertTrue(os.path.isfile(log))
        self.assertTrue(open(log).read().strip(), "pyjob_random")
        for f in jobs + [log]:
            os.unlink(f)

    # ================================================================================
    # ARRAY JOB SUBMISSIONS

    def test_kill_2(self):
        jobs = [make_script(["sleep 100"]) for _ in range(5)]
        array_script, array_jobs = prep_array_script(jobs, os.getcwd(), LoadSharingFacility.TASK_ID)
        jobid = LoadSharingFacility.sub(array_script, array=[1, 5], hold=True, log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        self.assertTrue(LoadSharingFacility.stat(jobid))
        LoadSharingFacility.kill(jobid)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_stat_2(self):
        jobs = [make_script(["sleep 100"]) for _ in range(5)]
        array_script, array_jobs = prep_array_script(jobs, os.getcwd(), LoadSharingFacility.TASK_ID)
        jobid = LoadSharingFacility.sub(array_script, array=[1, 5], hold=True, log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        data = LoadSharingFacility.stat(jobid)
        LoadSharingFacility.kill(jobid)
        self.assertTrue(data)
        self.assertEqual(jobid, int(data['job_number']))
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_3(self):
        jobs = [make_script(["sleep 1"]) for _ in range(5)]
        array_script, array_jobs = prep_array_script(jobs, os.getcwd(), LoadSharingFacility.TASK_ID)
        jobid = LoadSharingFacility.sub(array_script, array=[1, 5], hold=True, log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        time.sleep(5)
        self.assertTrue(LoadSharingFacility.stat(jobid))
        LoadSharingFacility.kill(jobid)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_4(self):
        directory = os.getcwd()
        jobs = [make_script([["sleep 5"], ['echo "file {0}"'.format(i)]], directory=directory)
                for i in range(5)]
        array_script, array_jobs = prep_array_script(jobs, directory, LoadSharingFacility.TASK_ID)
        jobid = LoadSharingFacility.sub(array_script, array=[1, 5], log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        while LoadSharingFacility.stat(jobid):
            time.sleep(1)
        for i, j in enumerate(jobs):
            f = j.replace(".sh", ".log")
            self.assertTrue(os.path.isfile(f))
            self.assertEqual("file {0}".format(i), open(f).read().strip())
            os.unlink(f)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_5(self):
        directory = os.getcwd()
        jobs = [make_script(['echo "file {0}"'.format(i)], directory=directory)
                for i in range(100)]
        array_script, array_jobs = prep_array_script(jobs, directory, LoadSharingFacility.TASK_ID)
        jobid = LoadSharingFacility.sub(array_script, array=[1, 100], log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        while LoadSharingFacility.stat(jobid):
            time.sleep(1)
        for i, j in enumerate(jobs):
            f = j.replace(".sh", ".log")
            self.assertTrue(os.path.isfile(f))
            self.assertEqual("file {0}".format(i), open(f).read().strip())
            os.unlink(f)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_6(self):
        jobs = [make_script(["echo $LSF_BINDIR"], directory=os.getcwd()) for _ in range(2)]
        array_script, array_jobs = prep_array_script(jobs, os.getcwd(), LoadSharingFacility.TASK_ID)
        jobid = LoadSharingFacility.sub(array_script, array=[1, 2], log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        while LoadSharingFacility.stat(jobid):
            time.sleep(1)
        for i, j in enumerate(jobs):
            f = j.replace(".sh", ".log")
            self.assertTrue(os.path.isfile(f))
            self.assertEqual(os.environ["LSF_BINDIR"], open(f).read().strip())
            os.unlink(f)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)

    def test_sub_7(self):
        assert "PYJOB_ENV1" not in os.environ
        os.environ["PYJOB_ENV1"] = "pyjob_random1"
        jobs = [make_script(["echo $PYJOB_ENV1"], directory=os.getcwd()) for _ in range(2)]
        array_script, array_jobs = prep_array_script(jobs, os.getcwd(), LoadSharingFacility.TASK_ID)
        jobid = LoadSharingFacility.sub(array_script, array=[1, 2], directory=os.getcwd(), log=os.devnull,
                                        name=inspect.stack()[0][3], shell="/bin/sh")
        while LoadSharingFacility.stat(jobid):
            time.sleep(1)
        for i, j in enumerate(jobs):
            f = j.replace(".sh", ".log")
            self.assertTrue(os.path.isfile(f))
            self.assertEqual(os.environ["PYJOB_ENV1"], open(f).read().strip())
            os.unlink(f)
        for f in jobs + [array_script, array_jobs]:
            os.unlink(f)


if __name__ == "__main__":
    unittest.main(verbosity=2)

