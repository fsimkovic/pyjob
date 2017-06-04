"""Testing facility for pyjob.misc.stopwatch"""

__author__ = "Felix Simkovic"
__date__ = "02 Jun 2017"

import time
import unittest

from pyjob.misc.stopwatch import StopWatch


class TestStopWatch(unittest.TestCase):

    def test_start_1(self):
        t = StopWatch()
        self.assertEqual(t.time, 0)

    def test_start_2(self):
        t = StopWatch()
        t.start()
        self.assertTrue(t.running)
        time.sleep(1)
        self.assertEqual(t.time, 1)

    def test_stop_1(self):
        t = StopWatch()
        t.start()
        time.sleep(1)
        t.stop()
        self.assertFalse(t.running)
        self.assertEqual(t.time, 1)

    def test_stop_2(self):
        t = StopWatch()
        t.start()
        time.sleep(1)   # <- count
        t.stop()
        self.assertEqual(t.time, 1)
        time.sleep(1)   # <- ignore
        t.start()
        time.sleep(2)   # <- count
        t.stop()
        self.assertEqual(t.time, 3)
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
        self.assertEqual(t.time, 4)
        self.assertEqual(t.nintervals, 3)

    def test_lap_1(self):
        t = StopWatch()
        self.assertEqual(t.lap, None)

    def test_lap_2(self):
        t = StopWatch()
        t.start()
        time.sleep(1)
        self.assertEqual(t.lap.time, 1)
        self.assertEqual(t[0].nlaps, 1)

    def test_lap_3(self):
        t = StopWatch()
        t.start()
        time.sleep(1)
        self.assertEqual(t.lap.time, 1)
        time.sleep(3)
        self.assertEqual(t.lap.time, 3)
        self.assertEqual(t[0].nlaps, 2)

    def test_lap_4(self):
        t = StopWatch()
        t.start()
        time.sleep(1)  # <- count
        self.assertEqual(t.lap.time, 1)
        time.sleep(3)  # <- count
        self.assertEqual(t.lap.time, 3)
        t.stop()
        time.sleep(1)  # <- ignore
        t.start()
        time.sleep(2)  # <- count
        self.assertEqual(t.lap.time, 2)
        t.stop()
        self.assertEqual(t.nintervals, 2)
        self.assertEqual(t[0].nlaps, 2)
        self.assertEqual(t[1].nlaps, 1)

    def test_reset_1(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        t.stop()
        self.assertEqual(t.time, 2)
        t.reset()
        self.assertEqual(t.time, 0)

    def test_runtime_1(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        t.stop()
        self.assertEqual(t.time, 2)

    def test_runtime_2(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        self.assertEqual(t.time, 2)

    def test_runtime_3(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        self.assertEqual(t.time, 2)
        time.sleep(2)
        self.assertEqual(t.time, 4)

    def test_runtime_4(self):
        t = StopWatch()
        t.start()
        time.sleep(2)
        self.assertEqual(t.time, 2)
        time.sleep(1)
        self.assertEqual(t.time, 3)
        time.sleep(1)
        self.assertEqual(t.time, 4)

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
        self.assertEqual(t.time, 4)

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
