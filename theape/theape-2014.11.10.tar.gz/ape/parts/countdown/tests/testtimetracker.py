
# python standard library
import unittest
import logging
from datetime import timedelta

# third party
from mock import patch, MagicMock, call
import numpy

# this package
from ape.parts.countdown.countdown import TimeTracker, INFO, DEBUG, STAT_STRING
from ape.parts.countdown.countdown import ELAPSED_STRING
from ape import ApeError


class TestingTimeTracker(unittest.TestCase):
    def setUp(self):
        # patch datetime
        self.datetime_patch = patch('datetime.datetime')
        self.datetime = self.datetime_patch.start()
        self.log_level = INFO
        self.logger = MagicMock()
        
        self.timer = TimeTracker(log_level=INFO)
        return

    def tearDown(self):
        """
        Stop the patches
        """
        self.datetime_patch.stop()
        return

    def test_constructor(self):
        """
        Does it build with the expected signature?
        """
        self.assertIsInstance(self.timer.logger, logging.Logger)
        self.assertEqual(self.timer.log_level, self.log_level)

        self.timer.log_level = 'aoeusnth'
        with self.assertRaises(ApeError):
            self.timer.log
        self.timer.log_level = DEBUG
        self.timer._logger = self.logger
        self.timer.log()
        self.logger.debug.assert_called_with()
        return

    def test_first_call(self):
        """
        Does it start the timer?
        """
        expected = 1234
        self.datetime.now.return_value  = expected
        self.assertIsNone(self.timer.start)
        self.assertTrue(self.timer())
        self.assertEqual(expected, self.timer.start)
        return

    def test_append(self):
        """
        Does it append an item to the numpy array?
        """
        self.assertEqual(self.timer.times, [])
        self.timer.append(3)
        self.assertTrue(all(numpy.array([3]) == self.timer.times))
        self.timer.append(7)
        self.assertTrue(all(numpy.array([3,7])==self.timer.times))
        return
    
    def test_stop_call(self):
        """
        Does it calculate the elapsed time?
        """
        self.timer._logger = self.logger
        times = [timedelta(seconds=5),
                 timedelta(seconds=9),
                 timedelta(seconds=40),
                 timedelta(seconds=60)]
        def side_effect():
            return times.pop(0)
        self.datetime.now.side_effect = side_effect
        self.timer()
        self.assertFalse(self.timer())

        delta = timedelta(seconds=4)
        self.assertEqual(self.timer.times, [4.0])

        calls = [call(ELAPSED_STRING.format(delta)),
                 call(STAT_STRING.format(min=delta,
                                                             q1=delta,
                                                             med=delta,
                                                             q3=delta,
                                                             max=delta,
                                                             mean=delta,
                                                             std=timedelta(0.0)))]
        self.assertEqual(self.logger.info.mock_calls, calls)
        self.assertIsNone(self.timer.start)
        self.assertEqual(delta, self.timer.percentile(0))
        self.assertTrue(self.timer())
        self.assertFalse(self.timer())
        self.assertEqual(timedelta(seconds=12),
                         self.timer.percentile(50))
        calls += [call(ELAPSED_STRING.format(timedelta(seconds=20))),
                  call(STAT_STRING.format(min=delta,
                                   q1=timedelta(seconds=8.0),
                                   med=timedelta(seconds=12.0),
                                   q3=timedelta(seconds=16.0),
                                   max=timedelta(seconds=20.0),
                                   mean=timedelta(seconds=12.0),
                                   std=timedelta(seconds=8.0)))]
        self.assertEqual(self.logger.info.mock_calls,
                         calls)
        # this doesn't work, there's a loss of precision with the timedelta conversions
        # the calculations need to be moved out and tested separately
        # or we can just say -- close enough
        return
