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

"""Module to store a stopwatch class"""

__author__ = "Felix Simkovic"
__date__ = "02 Jun 2017"
__version__ = "1.0"

import datetime
import logging
import time

logger = logging.getLogger(__name__)


class _Time(object):
    """Generic time class"""
    def __init__(self, index):
        """Instantiate a new :obj:`Lap`"""
        self.index = index
        self._start_time = 0.0
        self._end_time = 0.0

    def __repr__(self):
        return "{0}(index={1} time={2}s)".format(
            self.__class__.__name__, self.index, self.time)

    def __add__(self, other):
        """Add the lap times"""
        return self.time + other.time

    def __sub__(self, other):
        """Subtract the lap times"""
        return self.time - other.time

    @property
    def time(self):
        """Time"""
        return self._end_time - self._start_time

    @property
    def time_pretty(self):
        """Convert (seconds) to (days, hours, minutes, seconds)"""
        d = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=self.time)
        # Leave -1 in day as we start on the first day of the year
        return d.day - 1, d.hour, d.minute, d.second


class _Lap(_Time):
    """Lap time"""
    def __init__(self, index):
        """Instantiate a new :obj:`Lap`"""
        super(_Lap, self).__init__(index)


class _Interval(_Time):
    """Interval time"""

    def __init__(self, index):
        """Instantiate a new :obj:`Interval`"""
        super(_Interval, self).__init__(index)

        self._laps = []
        self._locked = False
        self._running = False

        self._ilap = 0

    def __getitem__(self, id):
        """Slice the intervals"""
        return self._laps[id]

    @property
    def average(self):
        """The average lap time in ms"""
        if len(self._laps) < 1:
            logger.critical("No laps taken!")
            return 0.0
        lap_times = [lap.time for lap in self._laps]
        return sum(lap_times) / float(len(lap_times))

    @property
    def lap(self):
        """Take a lap snapshot"""
        if self._locked:
            logger.critical("Cannot add a lap, interval finished!")
            return None
        elif not self._running:
            logger.critical("Cannot add a lap, interval not running!")
            return None

        self._ilap += 1
        lap = _Lap(self._ilap)
        lap._start_time = self._start_time + sum([l.time for l in self._laps])
        lap._end_time = time.time()
        self._laps += [lap]

        return lap

    @property
    def laps(self):
        """The laps"""
        return self._laps

    @property
    def nlaps(self):
        """Number of laps"""
        return len(self._laps)

    @property
    def time(self):
        """Total runtime"""
        if self._running:
            return int(round(time.time() - self._start_time))
        else:
            return int(round(self._end_time - self._start_time))

    def start(self):
        """Start the interval"""
        if self._running:
            logger.warning("Interval is running ...")
        elif self._locked:
            logger.warning("Interval is locked ...")
        else:
            logger.debug("Starting new interval ...")
            self._start_time = time.time()
            self._running = True

    def stop(self):
        """Stop the interval"""
        if self._running:
            logger.debug("Stopping interval ...")
            self._end_time = time.time()
            self._running = False
            self._locked = True
        else:
            logger.warning("Interval not running!")


class StopWatch(_Time):
    """Stopwatch class"""

    def __init__(self):
        """Instantiate a new :obj:`StopWatch`"""
        super(StopWatch, self).__init__(1)
        self.reset()

    def __getitem__(self, id):
        """Slice the intervals"""
        return self._intervals[id]

    def __repr__(self):
        return "{0}(time={1}s intervals={2})".format(
            self.__class__.__name__, self.time, len(self._intervals)
        )

    @property
    def intervals(self):
        """The intervals taken"""
        return self._intervals

    @property
    def lap(self):
        """Take a lap snapshot"""
        if len(self._intervals) > 0 and self._intervals[-1]._running:
            return self._intervals[-1].lap
        else:
            logger.critical("Cannot add a lap, stopwatch not running!")
            return None

    @property
    def nintervals(self):
        """Number of intervals"""
        return len(self._intervals)

    @property
    def running(self):
        """Stopwatch status"""
        return len(self._intervals) > 0 and self._intervals[-1]._running 

    @property
    def time(self):
        """Time in seconds"""
        return sum([interval.time for interval in self._intervals])

    @property
    def time_pretty(self):
        """Convert (seconds) to (days, hours, minutes, seconds)"""
        d = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=self.time)
        # Leave -1 in day as we start on the first day of the year
        return d.day - 1, d.hour, d.minute, d.second

    def reset(self):
        """Reset the timer"""
        self._intervals = []
        self._running = False
        self._iinterval = 0

    def start(self):
        """Start the interval"""
        if len(self._intervals) > 0 and self._intervals[-1]._running:
            logger.warning("Stopwatch already running!")
        else:
            logger.debug("Starting stopwatch ...")
            self._iinterval += 1
            interval = _Interval(self._iinterval)
            interval.start()
            self._intervals += [interval]
        return interval

    def stop(self):
        """Stop the interval"""
        if len(self._intervals) > 0 and self._intervals[-1]._running:
            logger.debug("Stopping stopwatch ...")
            self._intervals[-1].stop()
        else:
            logger.warning("Stopwatch not running!")
        return self._intervals[-1]
