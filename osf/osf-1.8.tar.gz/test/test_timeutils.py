import pytest
import osf.timeutils


def test_milliseconds_to_hhmmss():
    result = osf.timeutils.milliseconds_to_hhmmss(56011123)
    assert result == '15:33:31.123'


def test_milliseconds_to_hhmmss_sec_zero_fill():
    result = osf.timeutils.milliseconds_to_hhmmss(55981123)
    assert result == '15:33:01.123'


def test_milliseconds_to_hhmmss_min_zero_fill():
    result = osf.timeutils.milliseconds_to_hhmmss(54211123)
    assert result == '15:03:31.123'


def test_milliseconds_to_hhmmss_hr_zero_fill():
    result = osf.timeutils.milliseconds_to_hhmmss(18211123)
    assert result == '05:03:31.123'


def test_milliseconds_to_hhmmss_hun_zero_fill():
    result = osf.timeutils.milliseconds_to_hhmmss(18211011)
    assert result == '05:03:31.011'


def test_milliseconds_to_hhmmss_no_hundredths():
    result = osf.timeutils.milliseconds_to_hhmmss(18211000)
    assert result == '05:03:31.000'


def test_hhmmss_to_milliseconds():
    result = osf.timeutils.hhmmss_to_milliseconds(3, 31, 50, 123)
    assert result == 12710123
