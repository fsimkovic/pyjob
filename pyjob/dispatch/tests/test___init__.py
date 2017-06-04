"""Testing facility for pyjob.dispatch"""

__author__ = "Felix Simkovic"
__date__ = "10 May 2017"

import os
import sys
import unittest

from pyjob.dispatch import cexec


class Test(unittest.TestCase):

    def test_cexec_1(self):
        cmd = [sys.executable, "-c", "import sys; print(\"hello\"); sys.exit(0)"]
        stdout = cexec(cmd)
        self.assertEqual("hello", stdout)
    
    def test_cexec_2(self):
        cmd = [sys.executable, "-c", "import sys; sys.exit(1)"]
        self.assertRaises(RuntimeError, cexec, cmd)

    def test_cexec_3(self):
        cmd = [sys.executable, "-c", "import sys; print(\"hello\"); sys.exit(0)"]
        stdout = cexec(cmd, permit_nonzero=True)
        self.assertEqual("hello", stdout)
    
    def test_cexec_4(self):
        if sys.version_info < (3, 0):
            cmd = [sys.executable, "-c", "import sys; print(raw_input()); sys.exit(0)"]
        else:
            cmd = [sys.executable, "-c", "import sys; print(input()); sys.exit(0)"]
        stdout = cexec(cmd, stdin="hello")
        self.assertEqual("hello", stdout)

    def test_cexec_5(self):
        cmd = [sys.executable, "-c", "import os, sys; print(os.getcwd()); sys.exit(0)"]
        directory = os.path.join(os.getcwd(), 'pyjob', 'dispatch')
        stdout = cexec(cmd, directory=directory)
        self.assertEqual(directory, stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
