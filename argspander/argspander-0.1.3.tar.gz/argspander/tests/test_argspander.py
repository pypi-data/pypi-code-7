# noinspection PyInterpreter
import argspander


class TestExpand(object):
    @staticmethod
    def _test_unchanged(func):
        args = (1, 2, 3)
        kwargs = {"a": 1, "b": 2, "c": 3}
        assert(func(*args, **kwargs) == (args, kwargs))

    def test_decorated_function_no_expand_kwarg(self):
        @argspander.expand
        def _parrot(*args, **kwargs):
            return args, kwargs

        self._test_unchanged(_parrot)

    def test_decorated_method_no_expand_kwarg(self):
        class _ParrotClass(object):
            @argspander.expand
            def parrot(self, *args, **kwargs):
                return args, kwargs

        self._test_unchanged(_ParrotClass().parrot)

    @staticmethod
    def _test_arg_expansion(func):
        class Args(object):
            a = 1
            b = 2
            c = 3

        assert(func(Args(), expand=True) == (1, 2, 3))

    def test_decorated_function(self):
        @argspander.expand
        def _parrot(a, b, c):
            return a, b, c

        self._test_arg_expansion(_parrot)

    def test_decorated_method(self):
        class _ParrotClass(object):
            @argspander.expand
            def parrot(self, a, b, c):
                return a, b, c

        self._test_arg_expansion(_ParrotClass().parrot)
