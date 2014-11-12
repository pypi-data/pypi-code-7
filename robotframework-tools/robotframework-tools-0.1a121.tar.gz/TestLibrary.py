from __future__ import print_function

from robottools import testlibrary, ContextHandler


class Interface(ContextHandler):
    contexts = ['one', 'two']


_TestLibrary = testlibrary(context_handlers=[Interface])
keyword = _TestLibrary.keyword


class TestLibrary(_TestLibrary):
    @keyword.unicode_to_str
    def test(self, arg):
        print(repr(arg))


@keyword
@Interface.one
def test(self, arg):
    print('one', repr(arg))
