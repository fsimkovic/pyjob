"""Testing facility for pyjob.platform.lsf"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"

import glob
import inspect
import os
import sys
import time
import unittest

from pyjob.misc import make_script
from pyjob.platform.lsf import LoadSharingFacility


def skipUnless(condition, reason):
    if condition:
        return lambda x: x
    else:
        return lambda x: None 


@skipUnless("LSF_BINDIR" in os.environ, "not on LoadSharingFacility platform")
class TestLoadSharingFacility(unittest.TestCase):

    def test_stat_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3])
        time.sleep(5)
        data = LoadSharingFacility.stat(jobid)
        self.assertTrue(data)
        self.assertEqual(jobid, int(data['job_number']))
        LoadSharingFacility.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_stat_2(self):
        jobs = [make_script(["sleep 100"]) for _ in range(5)]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3])
        time.sleep(5)
        data = LoadSharingFacility.stat(jobid)
        LoadSharingFacility.kill(jobid)
        self.assertTrue(data)
        self.assertEqual(jobid, int(data['job_number']))
        for f in jobs + glob.glob(u'*.jobs') + glob.glob(u'*.script'):
            os.unlink(f)

    def test_kill_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3])
        time.sleep(5)
        self.assertTrue(LoadSharingFacility.stat(jobid))
        LoadSharingFacility.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_kill_2(self):
        jobs = [make_script(["sleep 100"]) for _ in range(5)]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3])
        time.sleep(5)
        self.assertTrue(LoadSharingFacility.stat(jobid))
        LoadSharingFacility.kill(jobid)
        for f in jobs + glob.glob(u'*.jobs') + glob.glob(u'*.script'):
            os.unlink(f)

    def test_rls_1(self):
        jobs = [make_script(["touch", "pyjob_rls_test_1"])]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3])
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

    def test_hold_1(self):
        jobs = [make_script(["sleep 100"])]
        jobid = LoadSharingFacility.sub(jobs, hold=False, name=inspect.stack()[0][3])
        time.sleep(5)
        LoadSharingFacility.hold(jobid)
        LoadSharingFacility.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_sub_1(self):
        jobs = [make_script(["sleep 1"])]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3])
        time.sleep(5)
        self.assertTrue(LoadSharingFacility.stat(jobid))
        LoadSharingFacility.kill(jobid)
        for f in jobs:
            os.unlink(f)

    def test_sub_2(self):
        jobs = [make_script(["sleep 1"]) for _ in range(5)]
        jobid = LoadSharingFacility.sub(jobs, hold=True, name=inspect.stack()[0][3])
        time.sleep(5)
        self.assertTrue(LoadSharingFacility.stat(jobid))
        LoadSharingFacility.kill(jobid)
        for f in jobs + glob.glob(u'*.jobs') + glob.glob(u'*.script'):
            os.unlink(f)

    def test_sub_3(self):
        directory = os.getcwd()
        jobs = [make_script([["sleep 5"], ['echo "file {0}"'.format(i)]], directory=directory)
                for i in range(5)]
        jobid = LoadSharingFacility.sub(jobs, name=inspect.stack()[0][3])
        start, timeout = time.time(), False
        while LoadSharingFacility.stat(jobid):
            # Don't wait too long, one minute, then fail
            if ((time.time() - start) // 60) >= 1:
                LoadSharingFacility.kill(jobid)
                timeout = True
            time.sleep(10)
        for f in jobs + glob.glob(u'*.jobs') + glob.glob(u'*.script'):
            os.unlink(f)
        if timeout:
            self.assertEqual(1, 0, "Timeout")
        else:
            for i, j in enumerate(jobs):
                f = j.replace(".sh", ".log")
                self.assertTrue(os.path.isfile(f))
                content = open(f).read().strip()
                self.assertEqual("file {0}".format(i), content)
                os.unlink(f)

    def test_sub_4(self):
        directory = os.getcwd()
        jobs = [make_script(['echo "file {0}"'.format(i)], directory=directory)
                for i in range(100)]
        jobid = LoadSharingFacility.sub(jobs, name=inspect.stack()[0][3])
        start, timeout = time.time(), False
        while LoadSharingFacility.stat(jobid):
            # Don't wait too long, one minute, then fail
            if ((time.time() - start) // 60) >= 1:
                LoadSharingFacility.kill(jobid)
                timeout = True
            time.sleep(10)
        time.sleep(20)
        for f in jobs + glob.glob(u'*.jobs') + glob.glob(u'*.script'):
            os.unlink(f)
        if timeout:
            self.assertEqual(1, 0, "Timeout")
        else:
            for i, j in enumerate(jobs):
                f = j.replace(".sh", ".log")
                self.assertTrue(os.path.isfile(f))
                content = open(f).read().strip()
                self.assertEqual("file {0}".format(i), content)
                os.unlink(f)

    def test_sub_5(self):
        jobs = [make_script(["echo $LSF_BINDIR"], directory=os.getcwd()) for _ in range(2)]
        jobid = LoadSharingFacility.sub(jobs, name=inspect.stack()[0][3])
        start, timeout = time.time(), False
        while LoadSharingFacility.stat(jobid):
            # Don't wait too long, one minute, then fail
            if ((time.time() - start) // 60) >= 1:
                LoadSharingFacility.kill(jobid)
                timeout = True
            time.sleep(10)
        for f in jobs + glob.glob(u'*.jobs') + glob.glob(u'*.script'):
            os.unlink(f)
        if timeout:
            self.assertEqual(1, 0, "Timeout")
        else:
            for i, j in enumerate(jobs):
                f = j.replace(".sh", ".log")
                self.assertTrue(os.path.isfile(f))
                content = open(f).read().strip()
                self.assertEqual(os.environ["LSF_BINDIR"], content)
                os.unlink(f)


if __name__ == "__main__":
    unittest.main(verbosity=2)

