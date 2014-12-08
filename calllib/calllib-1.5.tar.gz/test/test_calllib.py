import unittest

import calllib

class OkException(Exception): pass

class TestCase(unittest.TestCase):

    def test_free_function(self):
        def fn(foo, bar):
            if foo == 'foo' and bar == 'bar':
                raise OkException()

        self.assertRaises(OkException, calllib.apply, fn, {'foo':'foo', 'bar':'bar'})


    def test_free_function_with_defaults(self):
        def fn(foo, foo1='foo1', bar='notbar', baz='baz'):
            if foo == 'foo' and foo1 == 'foo1' and bar == 'bar' and baz == 'baz':
                raise OkException()

        self.assertRaises(OkException, calllib.apply, fn, {'foo':'foo', 'bar':'bar'})


    def test_free_function_with_missing_args(self):
        def fn(foo):
            pass

        self.assertRaises(ValueError, calllib.apply, fn, {})


    def test_return_value(self):
        def fn(x, y=10):
            return x+y
        self.assertEqual(calllib.apply(fn, {'x': 32}), 42)


    def test_bound_method(self):
        class C:
            def __init__(self):
                self.test = 'test'
            def func(self, foo):
                if foo == 'foo' and self.test == 'test':
                    raise OkException

        self.assertRaises(OkException, calllib.apply, C().func, {'foo': 'foo'})


    def test_bound_method_new_style(self):
        class C(object):
            def __init__(self):
                self.test = 'test'
            def func(self, foo):
                if foo == 'foo' and self.test == 'test':
                    raise OkException

        self.assertRaises(OkException, calllib.apply, C().func, {'foo': 'foo'})


    def test_unbound_method(self):
        class C:
            def __init__(self):
                self.test = 'test'
            def func(self, foo):
                if foo == 'foo' and self.test == 'test':
                    raise OkException

        o = C()
        self.assertRaises(OkException, calllib.apply, C.func, {'self': o, 'foo': 'foo'})


    def test_callable_instance(self):
        class C:
            def __init__(self):
                self.test = 'test'
            def __call__(self, foo):
                if foo == 'foo' and self.test == 'test':
                    raise OkException

        o = C()
        self.assertRaises(OkException, calllib.apply, o, {'foo': 'foo'})


    def test_callable_unbound(self):
        class C:
            def __init__(self):
                self.test = 'test'
            def __call__(self, foo):
                if foo == 'foo' and self.test == 'test':
                    raise OkException

        o = C()
        self.assertRaises(OkException, calllib.apply, C.__call__, {'self': o, 'foo': 'foo'})


    def test_uncallable_instance(self):
        class C:
            def __init__(self):
                self.test = 'test'

        o = C()
        self.assertRaises(TypeError, calllib.apply, o, {})


    def test_staticmethod(self):
        class C:
            @staticmethod
            def foo(a, b=3):
                if b == 3 and a == 10:
                    raise OkException

        self.assertRaises(OkException, calllib.apply, C().foo, {'a': 10})
        self.assertRaises(OkException, calllib.apply, C.foo, {'a': 10})


    def test_classmethod(self):
        class C:
            @classmethod
            def foo(cls, a, b=3):
                if cls is not C:
                    raise ValueError('unknown class %r' % C)
                if b == 3 and a == 10:
                    raise OkException

        self.assertRaises(OkException, calllib.apply, C().foo, {'a': 10})
        self.assertRaises(OkException, calllib.apply, C.foo, {'a': 10})


    def test_len(self):
        # can't call non-Python functions
        self.assertRaises(TypeError, calllib.apply, len, {})


    def test_class(self):
        class C:
            def __init__(self, foo):
                if foo == 'foo':
                    raise OkException

        self.assertRaises(OkException, calllib.apply, C, {'foo': 'foo'})

    def test_new_style_class(self):
        class C(object):
            def __init__(self, foo):
                if foo == 'foo':
                    raise OkException

        self.assertRaises(OkException, calllib.apply, C, {'foo': 'foo'})

    def test_no_init(self):
        # test old style
        class C():
            pass
        o = calllib.apply(C, {})
        self.assertIsInstance(o, C)

    def test_no_init_new_style(self):
        # and new style
        class C(object):
            pass
        o = calllib.apply(C, {})
        self.assertIsInstance(o, C)

    def test_derived(self):
        # ensure that base class __init__ functions are
        #  called
        class Base:
            def __init__(self, x):
                self.x = x

        class Derived(Base):
            pass

        # or that derived class __init__ functions are
        #  called
        class Derived1(Base):
            def __init__(self, x):
                self.x = x+1

        o = calllib.apply(Derived, {'x': 42})
        self.assertIsInstance(o, Derived)
        self.assertEqual(o.x, 42)

        o = calllib.apply(Derived1, {'x': 41})
        self.assertIsInstance(o, Derived1)
        self.assertEqual(o.x, 42)


    def test_derived_new_style(self):
        # ensure that base class __init__ functions are
        #  called
        class Base(object):
            def __init__(self, x):
                self.x = x

        class Derived(Base):
            pass

        # or that derived class __init__ functions are
        #  called
        class Derived1(Base):
            def __init__(self, x):
                self.x = x+1

        o = calllib.apply(Derived, {'x': 42})
        self.assertIsInstance(o, Derived)
        self.assertEqual(o.x, 42)

        o = calllib.apply(Derived1, {'x': 41})
        self.assertIsInstance(o, Derived1)
        self.assertEqual(o.x, 42)


    def test_no_call(self):
        class C:
            pass

        o = C()
        self.assertRaises(TypeError, calllib.apply, o, {})


class TestInspectParams(unittest.TestCase):
    def test_simple(self):
        def foo(): pass
        self.assertEqual(calllib.inspect_params(foo), ([], {}))

        def foo(x): pass
        self.assertEqual(calllib.inspect_params(foo), (['x'], {}))

        def foo(x, y=3): pass
        self.assertEqual(calllib.inspect_params(foo), (['x', 'y'], {'y': 3}))

        def foo(x, y=3, z=None): pass
        self.assertEqual(calllib.inspect_params(foo), (['x', 'y', 'z'], {'y': 3, 'z':None}))

        def foo(x=3): pass
        self.assertEqual(calllib.inspect_params(foo), (['x'], {'x': 3}))


class TestGetArgs(unittest.TestCase):
    def test_simple(self):
        def foo(): pass
        self.assertEqual(calllib.getargs(foo, {}), [])

        def foo(): pass
        self.assertEqual(calllib.getargs(foo, {'x': 3}), [])

        def foo(x=3): pass
        self.assertEqual(calllib.getargs(foo, {}), [3])

        def foo(x): pass
        self.assertEqual(calllib.getargs(foo, {'x': 3}), [3])

        def foo(x=3): pass
        self.assertEqual(calllib.getargs(foo, {'x': 4}), [4])

        def foo(x, y=3): pass
        self.assertEqual(calllib.getargs(foo, {'x': 4}), [4, 3])

        def foo(x, y=3): pass
        self.assertEqual(calllib.getargs(foo, {'x': 4, 'y': 5}), [4, 5])


    def test_errors(self):
        def foo(x, y=3): pass
        with self.assertRaises(ValueError):
            calllib.getargs(foo, {'y': 5})


class TestAll(unittest.TestCase):
    def test_all(self):
        import calllib

        # check that __all__ in the module contains everything that should be
        #  public, and only those symbols
        all = set(calllib.__all__)

        # check that things in __all__ only appear once
        self.assertEqual(len(all), len(calllib.__all__),
                         'some symbols appear more than once in __all__')

        # get the list of public symbols
        found = set(name for name in dir(calllib) if not name.startswith('_'))

        # make sure it matches __all__
        self.assertEqual(all, found)


unittest.main()
