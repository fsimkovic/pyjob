"""Test module for pyjob.platform.platform"""

__author__ = "Felix Simkovic"
__date__ = "03 Jun 2017"

import os
import unittest

from pyjob.platform.platform import Platform


class TestPlatform(unittest.TestCase):

    def test_prep_array_scripts_1(self):
        scripts = [os.path.join(os.getcwd(), "script1.sh"), os.path.join(os.getcwd(), "script2.sh")]
        array_script, array_jobs = Platform.prep_array_scripts(scripts, os.getcwd(), "SGE_TASK_ID")
        with open(array_jobs) as f_in:
            array_jobs_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(scripts, array_jobs_content)
        with open(array_script) as f_in:
            array_script_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(["#!/bin/sh", "script=`sed -n \"${SGE_TASK_ID}p\" " + array_jobs + "`",
                          "log=\"${script%.*}.log\"", "$script > $log"],
                         array_script_content)
        for f in [array_script, array_jobs]:
            os.unlink(f)

    def test_prep_array_scripts_2(self):
        scripts = [os.path.join(os.getcwd(), "script1.sh"), os.path.join(os.getcwd(), "script2.sh")]
        array_script, array_jobs = Platform.prep_array_scripts(scripts, os.getcwd(), "LSB_JOBINDEX")
        with open(array_jobs) as f_in:
            array_jobs_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(scripts, array_jobs_content)
        with open(array_script) as f_in:
            array_script_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(["#!/bin/sh", "script=`sed -n \"${LSB_JOBINDEX}p\" " + array_jobs + "`",
                          "log=\"${script%.*}.log\"", "$script > $log"],
                         array_script_content)
        for f in [array_script, array_jobs]:
            os.unlink(f)

    def test_prep_array_scripts_3(self):
        scripts = [os.path.join(os.getcwd(), "script1.sh"), os.path.join(os.getcwd(), "script2.sh")]
        array_script, array_jobs = Platform.prep_array_scripts(scripts, os.getcwd(), "RANDOM_TEXT")
        with open(array_jobs) as f_in:
            array_jobs_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(scripts, array_jobs_content)
        with open(array_script) as f_in:
            array_script_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(["#!/bin/sh", "script=`sed -n \"${RANDOM_TEXT}p\" " + array_jobs + "`",
                          "log=\"${script%.*}.log\"", "$script > $log"],
                         array_script_content)
        for f in [array_script, array_jobs]:
            os.unlink(f)

    def test_prep_array_scripts_4(self):
        scripts = [os.path.join(os.getcwd(), "script1.sh"), os.path.join(os.getcwd(), "script2.sh")]
        array_script, array_jobs = Platform.prep_array_scripts(scripts, "pyjob", "RANDOM_TEXT")
        self.assertEqual(os.path.abspath("pyjob"), os.path.dirname(array_script))
        self.assertEqual(os.path.abspath("pyjob"), os.path.dirname(array_jobs))
        with open(array_jobs) as f_in:
            array_jobs_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(scripts, array_jobs_content)
        with open(array_script) as f_in:
            array_script_content = [l.strip() for l in f_in.readlines()]
        self.assertEqual(["#!/bin/sh", "script=`sed -n \"${RANDOM_TEXT}p\" " + array_jobs + "`",
                          "log=\"${script%.*}.log\"", "$script > $log"],
                         array_script_content)
        for f in [array_script, array_jobs]:
            os.unlink(f)


if __name__ == "__main__":
    unittest.main(verbosity=2)

