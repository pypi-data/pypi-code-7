from cStringIO import StringIO
from nose.tools import eq_, raises
from sqlcapture.loghandler import LogFileHandler


def test_handler_format_json():
    handler = LogFileHandler('/tmp/foo', 'json')
    eq_(handler.formatter, handler.render_json)


def test_handler_format_plain():
    handler = LogFileHandler('/tmp/foo', 'plain')
    eq_(handler.formatter, handler.render_plain)


@raises(AssertionError)
def test_handler_format_invalid():
    LogFileHandler('/tmp/foo', 'plain_text')


def test_render_plain():
    handler = LogFileHandler('/tmp/foo', 'plain')
    queries = {
        'sql1': ['test1', 'test2'],
        'sql2': ['test1', 'test2', 'test3'],
    }
    expected = """\
-- test1
-- test2
sql1
-- test1
-- test2
-- test3
sql2
"""
    output = StringIO()
    handler.formatter(output, queries)
    output.seek(0)
    eq_(expected, output.read())


def test_render_json():
    handler = LogFileHandler('/tmp/foo', 'json')
    queries = {
        'sql1': ['test1', 'test2'],
        'sql2': ['test1', 'test2', 'test3'],
    }
    expected = (
        '{"sql1": ["test1", "test2"], '
        '"sql2": ["test1", "test2", "test3"]}'
    )
    output = StringIO()
    handler.formatter(output, queries)
    output.seek(0)
    eq_(expected, output.read())
