import pytest
import osf.classes


def test_str():
    line = osf.classes.OSFLine()
    line.time = 5111000
    line.text = "foo"
    line.link = "http://google.com/"
    line.tags = ['asd', 'foo']

    assert line.osf(5) == '----- 01:25:11.000 foo <http://google.com/> #asd #foo'


def test_str_no_tags():
    line = osf.classes.OSFLine()
    line.time = 5111000
    line.text = "foo"
    line.link = "http://google.com/"

    assert line.osf(5) == '----- 01:25:11.000 foo <http://google.com/>'


def test_str_no_link():
    line = osf.classes.OSFLine()
    line.time = 5111000
    line.text = "foo"

    assert line.osf(5) == '----- 01:25:11.000 foo'


def test_str_no_indentation():
    line = osf.classes.OSFLine()
    line.time = 5111000
    line.text = "foo"

    assert line.osf() == '01:25:11.000 foo'


def test_str_no_time():
    line = osf.classes.OSFLine()
    line.text = "foo"

    assert line.osf() == 'foo'


def test_str_no_time_plus_indent():
    line = osf.classes.OSFLine()
    line.text = "foo"

    assert line.osf(3) == '--- foo'
