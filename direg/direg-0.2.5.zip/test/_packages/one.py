# -*- coding: utf-8 -*-

from direg import get_value


class Foo:
    somevar = get_value('somevar')

    def meth(self):
        return get_value('somevar')

f = Foo()
assert f.meth() == 26804
assert f.somevar == 24742
assert Foo.somevar == 24742


def myfunc():
    somevar = get_value('somevar')
    return somevar

assert myfunc() == 16834

# #### FIXME: this case currently broken.
# def outer():
#     def inner():
#         somevar = get_value('somevar')
#         return somevar
#     return inner()
#
# assert outer() == 7678
