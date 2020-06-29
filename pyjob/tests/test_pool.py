import pytest

from pyjob.local import CPU_COUNT
from pyjob.pool import Pool


@pytest.mark.skipif(pytest.on_windows, reason="Deadlock on Windows")
class TestPool(object):
    def test_1(self):
        with Pool(processes=1) as pool:
            result = pool.map(pytest.helpers.fibonacci, [3, 4, 5])
        assert result == [1, 2, 3]

    def test_2(self):
        with Pool(processes=CPU_COUNT) as pool:
            result = pool.map(pytest.helpers.fibonacci, [1, 5, 10])
        assert result == [0, 3, 34]
