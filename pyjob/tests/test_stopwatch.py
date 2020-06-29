import time
import unittest

from pyjob.stopwatch import StopWatch


class TestStopWatch(object):
    def test_start_1(self):
        assert StopWatch().time == 0

    def test_start_2(self):
        sw = StopWatch()
        sw.start()
        assert sw.running
        time.sleep(1)
        assert round(sw.time) == 1.0

    def test_stop_1(self):
        sw = StopWatch()
        sw.start()
        time.sleep(1)
        sw.stop()
        assert not sw.running
        assert round(sw.time) == 1.0

    def test_stop_2(self):
        sw = StopWatch()
        sw.start()
        time.sleep(1)
        sw.stop()
        assert round(sw.time) == 1.0
        time.sleep(1)
        sw.start()
        time.sleep(2)
        sw.stop()
        assert round(sw.time) == 3.0
        assert sw.nintervals == 2

    def test_stop_3(self):
        sw = StopWatch()
        sw.start()
        time.sleep(1)
        sw.stop()
        time.sleep(1)
        sw.start()
        time.sleep(2)
        sw.stop()
        time.sleep(1)
        sw.start()
        time.sleep(1)
        sw.stop()
        assert round(sw.time) == 4.0
        assert sw.nintervals == 3

    def test_lap_1(self):
        assert StopWatch().lap is None

    def test_lap_2(self):
        sw = StopWatch()
        sw.start()
        time.sleep(1)
        assert round(sw.lap.time) == 1.0
        assert sw[0].nlaps == 1

    def test_lap_3(self):
        sw = StopWatch()
        sw.start()
        time.sleep(1)
        assert round(sw.lap.time) == 1.0
        time.sleep(3)
        assert round(sw.lap.time) == 3.0
        assert sw[0].nlaps == 2

    def test_lap_4(self):
        sw = StopWatch()
        sw.start()
        time.sleep(1)
        assert round(sw.lap.time) == 1.0
        time.sleep(3)
        assert round(sw.lap.time) == 3.0
        sw.stop()
        time.sleep(1)
        sw.start()
        time.sleep(2)
        assert round(sw.lap.time) == 2.0
        sw.stop()
        assert sw.nintervals == 2
        assert sw[0].nlaps == 2
        assert sw[1].nlaps == 1

    def test_reset_1(self):
        sw = StopWatch()
        sw.start()
        time.sleep(2)
        sw.stop()
        assert round(sw.time) == 2.0
        sw.reset()
        assert round(sw.time) == 0.0

    def test_runtime_1(self):
        sw = StopWatch()
        sw.start()
        time.sleep(2)
        sw.stop()
        assert round(sw.time) == 2.0

    def test_runtime_2(self):
        sw = StopWatch()
        sw.start()
        time.sleep(2)
        assert round(sw.time) == 2.0

    def test_runtime_3(self):
        sw = StopWatch()
        sw.start()
        time.sleep(2)
        assert round(sw.time) == 2.0
        time.sleep(2)
        assert round(sw.time) == 4.0

    def test_runtime_4(self):
        sw = StopWatch()
        sw.start()
        time.sleep(2)
        assert round(sw.time) == 2.0
        time.sleep(1)
        assert round(sw.time) == 3.0
        time.sleep(1)
        assert round(sw.time) == 4.0

    def test_runtime_5(self):
        sw = StopWatch()
        sw.start()
        time.sleep(2)
        time.sleep(1)
        sw.stop()
        time.sleep(2)
        sw.start()
        time.sleep(1)
        sw.stop()
        assert round(sw.time) == 4.0

    def test_convert_1(self):
        sw = StopWatch()
        sw.start()
        time.sleep(2)
        sw.stop()
        assert sw.time_pretty == (0, 0, 0, 2)

    def test_convert_2(self):
        sw = StopWatch()
        sw.start()
        time.sleep(5)
        sw.stop()
        assert sw.time_pretty == (0, 0, 0, 5)

    def test_context_1(self):
        with StopWatch() as sw:
            time.sleep(3)
        assert round(sw.time) == 3.0

    def test_context_2(self):
        with StopWatch() as sw:
            time.sleep(3)
            sw.stop()
            time.sleep(2)
        assert round(sw.time) == 3.0

    def test_context_3(self):
        with StopWatch() as sw:
            time.sleep(3)
            sw.stop()
            time.sleep(2)
            sw.start()
            time.sleep(1)
        assert round(sw.time) == 4.0
        assert [round(interval.time) for interval in sw.intervals] == [3.0, 1.0]
