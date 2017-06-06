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

"""Testing facility for pyjob"""

__author__ = "Felix Simkovic"
__date__ = "10 May 2017"

import os
import sys
import unittest

from pyjob import cexec


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
        directory = os.path.join(os.getcwd(), 'pyjob')
        stdout = cexec(cmd, directory=directory)
        self.assertEqual(directory, stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
