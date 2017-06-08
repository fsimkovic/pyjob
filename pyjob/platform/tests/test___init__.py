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

"""Test module for pyjob.platform"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"

import os
import unittest

from pyjob.platform import prep_array_script


class Test(unittest.TestCase):

    def test_prep_array_scripts_1(self):
        scripts = [os.path.join(os.getcwd(), "script1.sh"), os.path.join(os.getcwd(), "script2.sh")]
        array_script, array_jobs = prep_array_script(scripts, os.getcwd(), "SGE_TASK_ID")
        with open(array_jobs) as f_in:
            array_jobs_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(scripts, array_jobs_content)
        with open(array_script) as f_in:
            array_script_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual([
            "#!/bin/sh",
            'script=$(awk "NR==$SGE_TASK_ID" ' + array_jobs + ')',
            "log=$(echo $script | sed 's/.sh/.log/')",
            "$script > $log"
        ], array_script_content)
        for f in [array_script, array_jobs]:
            os.unlink(f)

    def test_prep_array_scripts_2(self):
        scripts = [os.path.join(os.getcwd(), "script1.sh"), os.path.join(os.getcwd(), "script2.sh")]
        array_script, array_jobs = prep_array_script(scripts, os.getcwd(), "LSB_JOBINDEX")
        with open(array_jobs) as f_in:
            array_jobs_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(scripts, array_jobs_content)
        with open(array_script) as f_in:
            array_script_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual([
            "#!/bin/sh",
            'script=$(awk "NR==$LSB_JOBINDEX" ' + array_jobs + ')',
            "log=$(echo $script | sed 's/.sh/.log/')",
            "$script > $log"
        ], array_script_content)
        for f in [array_script, array_jobs]:
            os.unlink(f)

    def test_prep_array_scripts_3(self):
        scripts = [os.path.join(os.getcwd(), "script1.sh"), os.path.join(os.getcwd(), "script2.sh")]
        array_script, array_jobs = prep_array_script(scripts, os.getcwd(), "RANDOM_TEXT")
        with open(array_jobs) as f_in:
            array_jobs_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(scripts, array_jobs_content)
        with open(array_script) as f_in:
            array_script_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual([
            "#!/bin/sh",
            'script=$(awk "NR==$RANDOM_TEXT" ' + array_jobs + ')',
            "log=$(echo $script | sed 's/.sh/.log/')",
            "$script > $log"
        ], array_script_content)
        for f in [array_script, array_jobs]:
            os.unlink(f)

    def test_prep_array_scripts_4(self):
        scripts = [os.path.join(os.getcwd(), "script1.sh"), os.path.join(os.getcwd(), "script2.sh")]
        array_script, array_jobs = prep_array_script(scripts, "pyjob", "RANDOM_TEXT")
        self.assertEqual(os.path.abspath("pyjob"), os.path.dirname(array_script))
        self.assertEqual(os.path.abspath("pyjob"), os.path.dirname(array_jobs))
        with open(array_jobs) as f_in:
            array_jobs_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(scripts, array_jobs_content)
        with open(array_script) as f_in:
            array_script_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual([
            "#!/bin/sh",
            'script=$(awk "NR==$RANDOM_TEXT" ' + array_jobs + ')',
            "log=$(echo $script | sed 's/.sh/.log/')",
            "$script > $log"
        ], array_script_content)
        for f in [array_script, array_jobs]:
            os.unlink(f)


if __name__ == "__main__":
    unittest.main(verbosity=2)

