"""
Ideas for decorator implemenations

"""

from StringIO import StringIO

from nose.tools import *
from metaconfig import ConfigDecorator, MetaConfig, Error


metaconfig_source = """
[metaconfig]
configs = test_dec

[test_dec:foo]
x = 42
y = 999
"""
mf = MetaConfig.from_config_fh(StringIO(metaconfig_source))

config = mf.get_config('test_dec')

# Include all defaults

def test_foo1():
    dec = ConfigDecorator(config)
    @dec.set_defaults(section='foo')
    def foo1(x, y):
        return x, y

    assert foo1() == ("42", "999")

# Include all defaults except some arguments
def test_foo2():
    dec = ConfigDecorator(config)
    @dec.set_defaults(section='foo', exclude='x')
    def foo2(x, y):
        return x, y

    assert foo2("2") == ("2", "999")
    assert_raises(TypeError, foo2)

# Include only specific arguments
def test_foo3():
    dec = ConfigDecorator(config)
    @dec.set_defaults(section='foo', include='y')
    def foo3(x, y):
        return x, y

    assert foo3("2") == ("2", "999")
    assert_raises(TypeError, foo3)

#---------------------------------------------------------------------------
# Since parameters with defaults must follow those witout defaults some 
# invocations of set_defaults should fail.
def test_exc1():
    dec = ConfigDecorator(config)
    def f():
        @dec.set_defaults(section='foo', include='x')
        def foo(x, y):
            return x, y
    assert_raises(Error, f)
def test_exc2():
    dec = ConfigDecorator(config)
    def f():
        @dec.set_defaults(section='foo', exclude='y')
        def foo(x, y):
            return x, y
    assert_raises(Error, f)

# If defaults are set in the function these won't fail
def test_exc3():
    dec = ConfigDecorator(config)
    def f():
        @dec.set_defaults(section='foo', include='x')
        def foo(x=None, y=None):
            return x, y
    assert f() == ("42", None)

def test_exc4():
    dec = ConfigDecorator(config)
    def f():
        @dec.set_defaults(section='foo', exclude='y')
        def foo(x=None, y=None):
            return x, y
    assert f() == ("42", None)

#---------------------------------------------------------------------------
# Set section in the decorator class
def test_foo4():
    foo_dec = ConfigDecorator(config, 'foo')
    @foo_dec.set_defaults()
    def foo4(x, y):
        return x, y

    assert foo4() == ("42", "999")

#---------------------------------------------------------------------------
# Set argument filters that can be used to do type conversion or validation
# In Python 3 this could you parameter annotations

# Set option x in foo to be of type int

def test_foo5():
    dec = ConfigDecorator(config)
    dec.set_filter('foo', 'x', int)
    
    @dec.set_defaults(section='foo')
    def foo5(x, y):
        return x, y

    assert foo5() == (42, "999")

# Set option s in foo to be of type int
def test_foo6():
    foo_dec = ConfigDecorator(config, 'foo')
    foo_dec.set_filter('x', float)

    @foo_dec.set_defaults()
    def foo6(x, y):
        return x, y

    assert foo6() == (42.0, "999")


#!TODO: Test for class methods.
