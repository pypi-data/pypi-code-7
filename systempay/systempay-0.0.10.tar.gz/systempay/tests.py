from unittest import TestCase
from datetime import datetime, date

from .client import SystempayMixin, TEST
from .utils import get_formatted_value


class SystempayTestCase(TestCase):

    def test_local_datetime_format(self):
        """
        Tests the locale datetime formatting
        """
        m = SystempayMixin('', '', TEST, 'Europe/Paris')

        self.assertEqual(
            m.get_local_datetime_format(datetime(2014, 10, 1, 12, 50, 25)),
            '2014-10-01T12:50:25+02:00')

        self.assertEqual(
            m.get_local_datetime_format(date(2014, 10, 30)),
            '2014-10-30T00:00:00+01:00')

        # DST
        self.assertEqual(
            m.get_local_datetime_format(datetime(2014, 10, 30, 12, 50, 25)),
            '2014-10-30T12:50:25+01:00')

    def test_utc_datetime_format(self):
        """
        Tests the UTC datetime formatting
        """
        m = SystempayMixin('', '', TEST, 'Europe/Paris')

        self.assertEqual(
            m.get_utc_datetime_format(datetime(2014, 10, 1, 12, 50, 25)),
            '2014-10-01T12:50:25+00:00')

        self.assertEqual(
            m.get_utc_datetime_format(date(2014, 10, 30)),
            '2014-10-30T00:00:00+00:00')

        self.assertEqual(
            m.get_utc_datetime_format(datetime(2014, 10, 30, 0, 0, 0)),
            '2014-10-30T00:00:00+00:00')

    def test_formatted_value(self):
        """
        Test formatted value for signature calculation
        """
        self.assertEqual(
            get_formatted_value(1),
            '1')

        self.assertEqual(
            get_formatted_value(datetime(2014, 10, 1, 12, 50, 25)),
            '20141001')

        self.assertEqual(
            get_formatted_value(datetime(2014, 10, 1)),
            '20141001')

        self.assertEqual(
            get_formatted_value('2014-10-01T00:00:25+02:00'),
            '20140930')

        self.assertEqual(
            get_formatted_value(True),
            '1')

        self.assertEqual(
            get_formatted_value(False),
            '0')
