import pytest
import osf
import osf.grammar
import modgrammar


def test_time_hhmmss():
    result = osf.grammar.Time.parser().parse_string('01:02:03.123')

    assert result.find(osf.grammar.HHMMSSTimeHourComponent).string == '01'
    assert result.find(osf.grammar.HHMMSSTimeMinuteComponent).string == '02'
    assert result.find(osf.grammar.HHMMSSSecondComponent).string == '03'
    assert result.find(osf.grammar.HHMMSSHundredthsComponent).string == '123'


def test_time_hhmmss_no_hundredths():
    result = osf.grammar.Time.parser().parse_string('01:02:03')

    assert result.find(osf.grammar.HHMMSSTimeHourComponent).string == '01'
    assert result.find(osf.grammar.HHMMSSTimeMinuteComponent).string == '02'
    assert result.find(osf.grammar.HHMMSSSecondComponent).string == '03'


def test_time_unix():
    result = osf.grammar.Time.parser().parse_string('1406359385')

    assert result.find(osf.grammar.UnixTime).string == '1406359385'


def test_line_basic():
    result = osf.parse_line("01:02:03   asd bla      <foo>   #bla     #foo")

    assert result.find(osf.grammar.HHMMSSTime).string == '01:02:03'
    assert result.find(osf.grammar.Text).string == 'asd bla'
    assert result.find(osf.grammar.Link)[1].string == 'foo'

    tags = result.find_all(osf.grammar.Tag)
    assert len(tags) == 2
    assert tags[0][1].string == 'bla'
    assert tags[1][1].string == 'foo'


def test_line_real():
    result = osf.parse_line("- 02:24:20  The Computer (How It Works)  <http://www.amazon.com/dp/072140619X/>   #shopping")

    assert len(result.find_all(osf.grammar.Indentation)) == 1

    assert result.find(osf.grammar.HHMMSSTime).string == '02:24:20'
    assert result.find(osf.grammar.Text).string == 'The Computer (How It Works)'
    assert result.find(osf.grammar.Link)[1].string == 'http://www.amazon.com/dp/072140619X/'

    tags = result.find_all(osf.grammar.Tag)
    assert len(tags) == 1
    assert tags[0][1].string == 'shopping'


def test_line_no_tags():
    result = osf.parse_line("01:02:03 asd bla <foo>")

    assert result.find(osf.grammar.HHMMSSTime).string == '01:02:03'
    assert result.find(osf.grammar.Text).string == 'asd bla'
    assert result.find(osf.grammar.Link)[1].string == 'foo'


def test_line_indentation():
    result = osf.parse_line("-- a")

    assert len(result.find_all(osf.grammar.Indentation)) == 2


def test_line_link_no_space():
    result = osf.parse_line("01:02:03 asd bla<foo>")

    assert result.find(osf.grammar.HHMMSSTime).string == '01:02:03'
    assert result.find(osf.grammar.Text).string == 'asd bla'
    assert result.find(osf.grammar.Link)[1].string == 'foo'

def test_line_no_link():
    result = osf.parse_line("01:02:03 asd bla")

    assert result.find(osf.grammar.HHMMSSTime).string == '01:02:03'
    assert result.find(osf.grammar.Text).string == 'asd bla'


def test_line_no_link_tag():
    result = osf.parse_line("01:02:03 asd bla #tag1 #tag2")

    tags = result.find_all(osf.grammar.Tag)
    assert len(tags) == 2
    assert tags[0][1].string == 'tag1'
    assert tags[1][1].string == 'tag2'


def test_line_tag_escape():
    result = osf.parse_line(r"01:02:03 asd \#bla")

    assert result.find(osf.grammar.HHMMSSTime).string == '01:02:03'
    assert result.find(osf.grammar.Text).string == r'asd \#bla'


def test_line_error():
    header, lines = osf.parse_lines([r"adsad#asd<<sadsd"])

    assert isinstance(lines[0], modgrammar.ParseError)


def test_lines():
    header, lines = osf.parse_lines(['A', '   ', 'B'])

    assert len(lines) == 2
    assert lines[0].find(osf.grammar.Text).string == 'A'
    assert lines[0]._line == 1
    assert lines[1].find(osf.grammar.Text).string == 'B'
    assert lines[1]._line == 3


def test_header():
    start, end, header = osf.parse_header([
        'HEADER',      # 0
        'foo',         # 1
        'bar1: foo1',  # 2
        'bar2:foo2',   # 3
        '',            # 4
        '/HEADER',     # 5
    ])

    assert start == 0
    assert end == 5
    assert len(header.v) == 1
    assert header.v[0] == 'foo'
    assert len(header.kv) == 2
    assert header.kv['bar1'] == 'foo1'
    assert header.kv['bar2'] == 'foo2'


def test_header_no_end():
    start, end, header = osf.parse_header([
        'HEADER',      # 0
        'foo',         # 1
        'bar1: foo1',  # 2
        'bar2:foo2',   # 3
    ])

    assert start == -1
    assert end == -1
    assert header is None


def test_header_with_line():
    header, lines = osf.parse_lines([
        'HEADER',
        'foo',
        '/HEADER',
        'A'
    ])

    assert header
    assert len(header.v) == 1
    assert header.v[0] == 'foo'
    assert len(lines) == 1
    assert lines[0].find(osf.grammar.Text).string == 'A'


