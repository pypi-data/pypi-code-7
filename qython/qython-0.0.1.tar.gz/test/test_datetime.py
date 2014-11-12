from datetime import datetime

from qython.datetime import timestamp


def test_timestamp():
    assert timestamp(datetime(2000, 5, 1)) == 957106800
