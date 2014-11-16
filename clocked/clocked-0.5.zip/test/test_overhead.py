""" Tests for Clocked. """


import timeit
import unittest
from clocked.clockit import Clocked
from clocked.decorators import clocked
from clocked.profiler_provider import ProfilerProvider
from clocked.settings import Settings


ITERATIONS = 200


class TestClocked(unittest.TestCase):

    def _assert(self, mini, val, maxi):
        self.assertTrue(
            mini <= val <= maxi,
            '{} <= {} <= {} is not true'.format(
                mini,
                val,
                maxi
            )
        )

    def _with(self):
        @clocked
        def _test():
            # noinspection PyUnusedLocal
            s = "test"
        for i in range(ITERATIONS):
            _test()
        _test()

    def _without(self):
        def _test():
            # noinspection PyUnusedLocal
            s = "test"
        for i in range(ITERATIONS):
            _test()
        _test()

    def test_comparison(self):
        without = self.get_without()
        with_off = self.get_with_off()
        with_on = self.get_with_on()

        print('without: {} ms ({} per ms)'.format(
            round(without * 1000.0, 2),
            round(ITERATIONS / (without * 1000.0), 2)
        ))
        print('with_off: {} ms ({} per ms)'.format(
            round(with_off * 1000.0, 2),
            round(ITERATIONS / (with_off * 1000.0), 2)
        ))
        print('with_on: {} ms ({} per ms)'.format(
            round(with_on * 1000.0, 2),
            round(ITERATIONS / (with_on * 1000.0), 2)
        ))
        print('ratios: {} -> {} -> {}'.format(
            round(with_on / without, 1),
            round(with_on / with_off, 1),
            '1'
        ))

    def get_without(self):
        t = timeit.Timer(self._without)
        t.timeit(100)
        elapsed = t.timer()
        return elapsed

    def get_with_off(self):
        Settings._profiler_provider = None
        ProfilerProvider._profiler = None
        t = timeit.Timer(self._with)
        t.timeit(100)
        elapsed = t.timer()
        return elapsed

    def get_with_on(self):
        Clocked.initialize('template')
        t = timeit.Timer(self._with)
        t.timeit(100)
        elapsed = t.timer()
        return elapsed
