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

"""Testing facility for .local"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"

import os
import time
import unittest

from pyjob.misc import make_python_script
from pyjob.platform.local import LocalJobServer, SERVER_INDEX 


class TestLocalJobServer(unittest.TestCase):

    def test_sub_1(self):
        j = make_python_script([
            ["import sys, time"], 
            ["print(\"I am job: 1\")"],
            ["sys.exit(0)"],
        ], prefix="unittest")
        l = j.rsplit('.', 1)[0] + '.log'
        LocalJobServer.sub([j], nproc=1)
        time.sleep(0.5)
        self.assertTrue(os.path.isfile(l))
        for f in [j, l]: os.unlink(f)

    def test_sub_2(self):
        jobs = [
            make_python_script([
                ["import sys, time"], 
                ["print(\"I am job: {0}\")".format(i)],
                ["sys.exit(0)"],
            ], prefix="unittest") for i in range(6)
        ]
        logs = [j.rsplit('.', 1)[0] + '.log' for j in jobs]
        LocalJobServer.sub(jobs, nproc=2)
        time.sleep(0.5)
        self.assertTrue(os.path.isfile(logs[-1]))
        for f in jobs + logs: os.unlink(f)
    
    def test_kill_1(self):
        jobs = [
            make_python_script([
                ["import sys, time"], 
                ["time.sleep(100)"],
                ["sys.exit(0)"],
            ], prefix="unittest") for i in range(6)
        ]
        logs = [j.rsplit('.', 1)[0] + '.log' for j in jobs]
        jobid = LocalJobServer.sub(jobs, nproc=2)
        time.sleep(0.5)
        self.assertTrue(jobid in SERVER_INDEX)
        LocalJobServer.kill(jobid)
        self.assertFalse(jobid in SERVER_INDEX)
        for l in logs:
            self.assertFalse(os.path.isfile(l))
        for f in jobs: os.unlink(f)
     

if __name__ == "__main__":
    unittest.main(verbosity=2)

