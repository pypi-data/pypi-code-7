from markey.rules import ruleset, include, rule, bygroups
from markey.machine import iter_rules, tokenize, parse_arguments
from markey.tools import Token, TokenStream
from markey.underscore import rules as underscore_rules


def test_parse_arguments():
    line = '<% gettext("some string", str="foo")'
    stream = TokenStream.from_tuple_iter(tokenize(line, underscore_rules))
    stream.next()
    stream.next()
    stream.expect('gettext_begin')
    funcname = stream.expect('func_name').value
    args, kwargs = parse_arguments(stream, 'gettext_end')
    assert args == ('some string',)
    assert kwargs == {'str': 'foo'}
