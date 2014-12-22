
# python standard library
import unittest
import random
from datetime import timedelta
import datetime

# third-party
from mock import MagicMock, patch, call
import numpy

# this package
from ape.parts.countdown.countdown import CountdownTimer, INFO, ESTIMATED_REMAINING


class TestCountdownTimer(unittest.TestCase):
    def setUp(self):
        # patch datetime
        self.datetime_patch = patch('datetime.datetime')
        self.datetime = self.datetime_patch.start()
        self.log_level = INFO
        self.logger = MagicMock()        

        self.repetitions = random.randrange(1, 100)
        self.timer = CountdownTimer(repetitions=self.repetitions, log_level=INFO)
        return

    def tearDown(self):
        """
        Stop the patches
        """
        self.datetime_patch.stop()
        return

    def test_constructor(self):
        """
        Does it build?
        """
        self.assertEqual(self.timer.repetitions, self.repetitions)
        self.assertEqual(self.timer.log_level, INFO)
        self.assertIsNone(self.timer.start)
        self.assertIsNone(self.timer.last_time)
        self.assertIsNone(self.timer._times)

        timer = CountdownTimer(end_time=2)
        self.assertEqual(2, timer.end_time)

        timer = CountdownTimer(total_time=4)
        self.assertEqual(4, timer.total_time)
        return

    def test_time_remains_no_parameters(self):
        """
        Does it return False if None of the parameters is set?
        """
        # this is vacuously true until the other cases are implemented
        timer = CountdownTimer(end_time = None, total_time = None, repetitions=None)
        self.assertFalse(timer.time_remains())
        return

    def test_time_remains_end_time(self):
        """
        Does it evaluate the cases where end-time is set correctly?
        """
        end_time = random.randint(5, 100)
        timer = CountdownTimer(end_time=end_time, total_time=None, repetitions=None)
        self.datetime.now.return_value = end_time - 1
        self.assertTrue(timer.time_remains())
        self.datetime.now.return_value = end_time + 1
        self.assertFalse(timer.time_remains())

        # add repetitions
        # out of repetitions quits even if there is still time
        timer.repetitions = 1
        self.datetime.now.return_value = end_time - 1
        self.assertFalse(timer.time_remains())

        # end-time takes precedence over repetitions
        self.datetime.now.return_value = end_time + 1
        timer.repetitions = 2
        self.assertFalse(timer.time_remains())

        # make sure it doesn't accidentally quit prematurely
        timer.repetitions = 2
        self.datetime.now.return_value = end_time - 1
        self.assertTrue(timer.time_remains())

        # add total time to the mix
        timer.total_time = timer.end_time - 10
        timer.start = 0
        timer.repetitions = 10
        # repetitions and end-time won't quit, total time does
        self.assertFalse(timer.time_remains())

        # but end-time takes precedence over total-time
        self.datetime.now.return_value = end_time + 1
        timer.start = end_time + 1 # elapsed time will be 0
        self.assertFalse(timer.time_remains())

        # and repetitions will quit if there's time
        self.datetime.now.return_value = end_time - 1
        timer.start = end_time - 1
        timer.repetitions = 1
        self.assertFalse(timer.time_remains())
        return

    def test_time_remains_total_time(self):
        """
        Does it work if the total-time is set?
        """
        total_time = random.randrange(10,100)
        timer = CountdownTimer(total_time=total_time,
                               repetitions=None,
                               end_time=None)

        # does time-out return False?
        timer.start = 0
        self.datetime.now.return_value = total_time
        self.assertFalse(timer.time_remains())

        # if there's still time, does it continue
        timer.start = total_time
        self.datetime.now.return_value = total_time
        self.assertTrue(timer.time_remains())

        # if time-remains but not repetitions, will it time-out?
        timer.repetitions = 1
        self.assertFalse(timer.time_remains())
        return
    
    def test_close(self):
        """
        Does it reset the attributes?
        """        
        timer = CountdownTimer(repetitions=10, end_time=40, total_time=100)
        timer.start = 300
        timer.close()
        self.assertIsNone(timer.start)
        self.assertIsNone(timer.end_time)
        self.assertIsNone(timer.total_time)
        self.assertEqual(0, timer.repetitions)
        return

    def test_log_estimated_time_remaining(self):
        """
        Does it calculate the remaining estimate?
        """
        timer = CountdownTimer(repetitions=None, log_level=INFO)
        timer._logger = self.logger
        timer.log_estimated_time_remaining()
        calls = [call(ESTIMATED_REMAINING.format(0))]
        self.assertEqual(self.logger.info.mock_calls, calls)
        
        timer.repetitions = 3
        timer._times = ([0,5,10])
        timer.log_estimated_time_remaining()
        calls.append(call(ESTIMATED_REMAINING.format(timedelta(seconds=15))))
        self.assertEqual(calls, self.logger.info.mock_calls)
        
        timer.total_time = timedelta(seconds=5)
        self.datetime.now.return_value = timedelta(seconds=10)
        timer.start = timedelta(seconds=8)
        
        ## elapsed = 2, remaining = 3
        timer.log_estimated_time_remaining()
        calls.append(call(ESTIMATED_REMAINING.format(timedelta(seconds=3))))
        self.assertEqual(calls, self.logger.info.mock_calls)

        # add end_time
        timer.end_time = timedelta(seconds=11)
        timer.log_estimated_time_remaining()
        calls.append(call(ESTIMATED_REMAINING.format(timedelta(seconds=1))))
        self.assertEqual(calls, self.logger.info.mock_calls)
        return

    def test_call(self):
        """
        Does it keep track of time for the right number of repetitions?
        """
        # first repetition
        now = first_now = timedelta(seconds=10)
        self.datetime.now.return_value = first_now

        self.assertTrue(self.timer())
        
        self.datetime.now.assert_called_with()              
        self.assertEqual(self.timer.start, first_now)
        self.assertEqual(self.timer.last_time, first_now)
        self.assertEqual(self.timer.repetitions, self.repetitions)

        for repetition in xrange(1, self.repetitions):
            now +=  first_now
            self.datetime.now.return_value = now
            self.assertTrue(self.timer())
            self.assertEqual((first_now).total_seconds(), self.timer.times[repetition-1])
            self.assertEqual(self.timer.last_time, now)
            self.assertEqual(self.timer.repetitions, self.repetitions - repetition)
            self.assertTrue(all(numpy.array([10.] * repetition) == self.timer.times))

        # last repetition
        now += first_now
        self.datetime.now.return_value = now
        self.assertFalse(self.timer())

        self.assertEqual(self.timer.last_time, now)
        self.assertEqual(0, self.timer.repetitions)

        self.assertIsNone(self.timer.start)
        self.assertIsNone(self.timer._times)
        return
