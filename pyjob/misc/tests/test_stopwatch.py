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

"""Testing facility for pyjob.misc.stopwatch"""

__author__ = "Felix Simkovic"
__date__ = "02 Jun 2017"

import time
import unittest

from pyjob.misc.stopwatch import StopWatch


class TestStopWatch(unittest.TestCase):

    def test_start_1(self):
        t = StopWatch()
        self.assertEqual(int(round(t.time)), 0)

    def test_start_2(self):
        t = StopWatch()
        t.start()
        self.assertTrue(t.running)
        time.sleep(1)
        self.assertEqual(int(round(t.time)), 1)

    def test_stop_1(self):
        t = StopWatch()
        t.start()
        time.sleep(1)
        t.stop()
        self.assertFalse(t.running)
        self.assertEqual(int(round(t.time)), 1)

    def test_stop_2(self):
        t = StopWatch()
        t.start()
        time.sleep(1)   # <- count
        t.stop()
        self.assertEqual(int(round(t.time)), 1)
        time.sleep(1)   # <- ignore
        t.start()
        time.sleep(2)   # <- count
        t.stop()
        self.assertEqual(int(round(t.time)), 3)
        self.assertEqual(t.nintervals, 2)

    def test_stop_3(self):
        t = StopWatch()
        t.start()
        time.sleep(1)  # <- count
        t.stop()
        time.sleep(1)  # <- ignore
        t.start()
        time.sleep(2)  # <- count
        t.stop()
        time.sleep(1)  # <- ignore
        t.start()
        time.sleep(1)  # <- count
        t.stop()
        self.assertEqual(int(round(t.time)), 4)
        self.assertEqual(t.nintervals, 3)

    def test_lap_1(self):
        t = StopWatch()
        self.assertEqual(t.lap, None)

    def test_lap_2(self):
        t = StopWatch()
        t.start()
        time.sleep(1)
        self.assertEqual(int(round(t.lap.time)), 1)
        self.assertEqual(t[0].nlaps, 1)

    def test_lap_3(self):
        t = StopWatch()
        t.start()
        time.sleep(1)
        self.assertEqual(int(round(t.lap.time)), 1)
        time.sleep(3)
        self.assertEqual(int(round(t.lap.time)), 3)
        self.assertEqual(t[0].nlaps, 2)

    def test_lap_4(self):
        t = StopWatch()
        t.start()
        time.sleep(1)  # <- count
        self.assertEqual(int(round(t.lap.time)), 1)
        time.sleep(3)  # <- count
        self.assertEqual(int(round(t.lap.time)), 3)
        t.stop()
        time.sleep(1)  # <- ignore
        t.start()
        time.sleep(2)  # <- count
        self.assertEqual(int(round(t.lap.time)), 2)
        t.stop()
        self.assertEqual(t.nintervals, 2)
        self.assertEqual(t[0].nlaps, 2)
        self.assertEqual(t[1].nlaps, 1)

    def test_reset_1(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        t.stop()
        self.assertEqual(int(round(t.time)), 2)
        t.reset()
        self.assertEqual(int(round(t.time)), 0)

    def test_runtime_1(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        t.stop()
        self.assertEqual(int(round(t.time)), 2)

    def test_runtime_2(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        self.assertEqual(int(round(t.time)), 2)

    def test_runtime_3(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        self.assertEqual(int(round(t.time)), 2)
        time.sleep(2)
        self.assertEqual(int(round(t.time)), 4)

    def test_runtime_4(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        self.assertEqual(int(round(t.time)), 2)
        time.sleep(1)
        self.assertEqual(int(round(t.time)), 3)
        time.sleep(1)
        self.assertEqual(int(round(t.time)), 4)

    def test_runtime_5(self):
        t = StopWatch()
        t.start()
        time.sleep(2)   # <- count
        time.sleep(1)   # <- count
        t.stop()
        time.sleep(2)   # <- ignore
        t.start()
        time.sleep(1)   # <- count
        t.stop()
        self.assertEqual(int(round(t.time)), 4)

    def test_convert_1(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        t.stop()
        self.assertEqual((0, 0, 0, 2), t.time_pretty)

    def test_convert_2(self):
        t = StopWatch()
        t.start()
        time.sleep(5)
        t.stop()
        self.assertEqual((0, 0, 0, 5), t.time_pretty)


if __name__ == "__main__":
    unittest.main(verbosity=2)
