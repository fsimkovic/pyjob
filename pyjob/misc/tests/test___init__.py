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

"""Testing facility for pyjob.misc.__init__"""

__author__ = "Felix Simkovic"
__date__ = "29 May 2017"

import os
import shutil
import unittest

from pyjob.misc import tmp_dir, tmp_file


class Test(unittest.TestCase):

    def test_tmp_dir_1(self):
        tmp = tmp_dir()
        self.assertTrue(os.path.isdir(tmp))
        shutil.rmtree(tmp)

    def test_tmp_dir_2(self):
        tmp = tmp_dir(directory=os.getcwd())
        self.assertTrue(os.path.isdir(tmp))
        path, _ = os.path.split(tmp)
        self.assertEqual(os.getcwd(), path)
        shutil.rmtree(tmp)

    def test_tmp_dir_3(self):
        tmp = tmp_dir(prefix="first")
        self.assertTrue(os.path.isdir(tmp))
        _, name = os.path.split(tmp)
        self.assertTrue(name.startswith("first"))
        shutil.rmtree(tmp)

    def test_tmp_dir_4(self):
        tmp = tmp_dir(suffix="last")
        self.assertTrue(os.path.isdir(tmp))
        _, name = os.path.split(tmp)
        self.assertTrue(name.endswith("last"))
        shutil.rmtree(tmp)

    def test_tmp_dir_5(self):
        tmp = tmp_dir(suffix="simbad.the-last")
        self.assertTrue(os.path.isdir(tmp))
        _, name = os.path.split(tmp)
        self.assertTrue(name.endswith("simbad.the-last"))
        shutil.rmtree(tmp)

    def test_tmp_dir_6(self):
        tmp = tmp_dir(directory=os.getcwd(), prefix="first", suffix="last")
        self.assertTrue(os.path.isdir(tmp))
        path, name = os.path.split(tmp)
        self.assertEqual(os.getcwd(), path) 
        self.assertTrue(name.startswith("first"))
        self.assertTrue(name.endswith("last"))
        shutil.rmtree(tmp)

    def test_tmp_file_1(self):
        tmp = tmp_file()
        self.assertTrue(os.path.isfile(tmp))
        os.remove(tmp)

    def test_tmp_file_2(self):
        tmp = tmp_file(delete=True)
        self.assertFalse(os.path.isfile(tmp))

    def test_tmp_file_3(self):
        tmp = tmp_file(directory=os.getcwd())
        self.assertTrue(os.path.isfile(tmp))
        path, _ = os.path.split(tmp)
        self.assertEqual(os.getcwd(), path)
        os.remove(tmp)

    def test_tmp_file_4(self):
        tmp = tmp_file(prefix="first")
        self.assertTrue(os.path.isfile(tmp))
        self.assertTrue(os.path.basename(tmp).startswith("first"))
        os.remove(tmp)

    def test_tmp_file_5(self):
        tmp = tmp_file(stem="middle")
        self.assertTrue(os.path.isfile(tmp))
        self.assertTrue("middle" in os.path.basename(tmp))
        os.remove(tmp)

    def test_tmp_file_6(self):
        tmp = tmp_file(suffix="last")
        self.assertTrue(os.path.isfile(tmp))
        self.assertTrue(os.path.basename(tmp).endswith("last"))
        os.remove(tmp)

    def test_tmp_file_7(self):
        tmp = tmp_file(delete=True, stem="middle")
        self.assertFalse(os.path.isfile(tmp))
        self.assertTrue("middle" in os.path.basename(tmp))

    def test_tmp_file_8(self):
        tmp = tmp_file(delete=False, directory=os.getcwd(), prefix="first", stem="middle", suffix="last")
        self.assertTrue(os.path.isfile(tmp))
        path, name = os.path.split(tmp)
        self.assertEqual(os.getcwd(), path)
        self.assertTrue(name.startswith("first"))
        self.assertTrue("middle" in name)
        self.assertTrue(name.endswith("last"))
        os.remove(tmp)
    
    def test_tmp_file_9(self):
        tmp = tmp_file(delete=False, directory=os.getcwd(), prefix="first", suffix="last")
        self.assertTrue(os.path.isfile(tmp))
        path, name = os.path.split(tmp)
        self.assertEqual(os.getcwd(), path)
        self.assertTrue(name.startswith("first"))
        self.assertTrue(name.endswith("last"))
        os.remove(tmp)
    

if __name__ == "__main__":
    unittest.main(verbosity=2)

