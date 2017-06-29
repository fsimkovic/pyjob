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

"""Testing facility for pyjob.job"""

__author__ = "Felix Simkovic"
__date__ = "06 May 2017"

import glob
import os
import unittest

from pyjob.exception import PyJobError
from pyjob.job import Job
from pyjob.misc import SCRIPT_EXT, make_script, tmp_file

# Only need to check two, one for cluster and local
platform = "sge" if "SGE_ROOT" in os.environ else "local"


class TestJob(unittest.TestCase):

    def test_submit_1(self):
        ss = make_script(["sleep 1"])
        ls = ss.replace(SCRIPT_EXT, ".log")
        j = Job(platform)
        j.submit(ss, nproc=2, log=ls)
        j.wait()
        for f in [ss, ls]:
            os.unlink(f)

    def test_submit_2(self):
        ss = [make_script(["sleep 1"])]
        ls = [ss[0].replace(SCRIPT_EXT, ".log")]
        j = Job(platform)
        j.submit(ss, nproc=2, log=ls[0])
        j.wait()
        for f in ss + ls:
            os.unlink(f)

    def test_submit_3(self):
        ss = [make_script(["sleep 1"]) for _ in range(5)]
        ls = [f.replace(SCRIPT_EXT, ".log") for f in ss]
        j = Job(platform)
        j.submit(ss, nproc=2, log=os.devnull)
        j.wait()
        for f in ss + ls + glob.glob("array_*"):
            os.unlink(f)

    def test_check_script_1(self):
        ss = [make_script(["sleep 1"])]
        ls = [f.replace(SCRIPT_EXT, ".log") for f in ss]
        s, l = Job.check_script(ss)
        self.assertEqual(ss, s)
        self.assertEqual(ls, l)
        for f in ss:
            os.unlink(f)

    def test_check_script_2(self):
        ss = [make_script(["sleep 1"]) for _ in range(5)]
        ls = [f.replace(SCRIPT_EXT, ".log") for f in ss]
        s, l = Job.check_script(ss)
        self.assertEqual(ss, s)
        self.assertEqual(ls, l)
        for f in ss:
            os.unlink(f)

    def test_check_script_3(self):
        ss = make_script(["sleep 1"])
        ls = ss.replace(SCRIPT_EXT, ".log")
        s, l = Job.check_script(ss)
        self.assertEqual([ss], s)
        self.assertEqual([ls], l)
        os.unlink(ss)

    def test_check_script_4(self):
        ss = tmp_file(delete=False)
        with open(ss, "w") as f_out:
            f_out.write("sleep 1")
        self.assertRaises(PyJobError, Job.check_script, ss)


if __name__ == "__main__":
    unittest.main(verbosity=2)
