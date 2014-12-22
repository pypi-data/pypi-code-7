
# python standard library
import unittest
import datetime
import random

# third-party
from mock import MagicMock, patch

# this package
from ape.parts.sleep.sleep import TheBigSleep
from ape import ApeError


class TestTheBigSleep(unittest.TestCase):
    def setUp(self):
        self.end = MagicMock()
        self.total = MagicMock()
        self.interval = random.randint(1, 100)
        self.sleep = TheBigSleep(end=self.end,
                                 total=self.total,
                                 interval=self.interval)        
        return

    def test_constructor(self):
        """
        Does it have the expected signature?
        """
        self.assertEqual(self.sleep.end, self.end)
        self.assertEqual(self.sleep.total, self.total)
        self.assertEqual(self.sleep.interval, self.interval)

        # test the defaults
        sleep = TheBigSleep()
        self.assertIsNone(sleep.end)
        self.assertIsNone(sleep.total)
        self.assertEqual(sleep.interval, 1)
        return

    def test_then(self):
        """
        Does it correctly set 'then'
        """
        sleep = TheBigSleep()

        # neither set
        with self.assertRaises(ApeError):
            sleep.then

        # end is set
        end = MagicMock()
        sleep.end = end
        self.assertEqual(sleep.then, end)

        # total only is set
        sleep.end = None
        total = MagicMock(spec='datetime.timedelta')
        sleep.total = total
        now = MagicMock(id='now')
        summation = MagicMock(id='now and then')
        future = MagicMock(id='now_call')
        now.now.return_value = future
        future.__add__.return_value = summation

        with patch('datetime.datetime', now):
            self.assertEqual(sleep.then, summation)

        # both set
        sleep.end = end
        self.assertEqual(sleep.end, end)

        # total is set to a bad value
        sleep.end = None
        sleep.total = 5
        with self.assertRaises(ApeError):
            sleep.then
        return

    def test_setters(self):
        """
        Do they reset then?
        """
        self.assertIsNotNone(self.sleep.then)
        self.sleep.end = None
        self.assertIsNone(self.sleep._then)
        self.assertIsNotNone(self.sleep.then)
        self.sleep.total = None
        self.assertIsNone(self.sleep._then)
        return

    def test_zero(self):
        """
        Is zero a 0 timedelta?
        """
        positive = datetime.timedelta(seconds=random.randint(1,100))
        negative = datetime.timedelta(seconds=random.randint(-100, -1))
        zero = datetime.timedelta(seconds=0)
        self.assertGreater(positive, self.sleep.zero)
        self.assertLessEqual(negative, self.sleep.zero)
        self.assertEqual(zero, self.sleep.zero)
        return

    def test_timer(self):
        """
        Does it build an event timer with the interval set correclty?
        """
        self.assertEqual(self.interval, self.sleep.timer.seconds)
        return

    def test_close(self):
        """
        Does it set self.then to zero so it stops and call the timer.close?
        """
        timer = MagicMock()
        self.sleep._timer = timer
        self.sleep.close()
        timer.close.assert_called_with()
        self.assertEqual(self.sleep.then, self.sleep.zero)
        return
        
# end class TestTheBigSleep        
