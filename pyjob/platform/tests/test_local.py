"""Testing facility for .local"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"

import os
import time
import unittest

from pyjob.misc import make_python_script
from pyjob.platform.local import LocalJobServer


class TesLocalJobServer(unittest.TestCase):

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
     

if __name__ == "__main__":
    unittest.main(verbosity=2)

