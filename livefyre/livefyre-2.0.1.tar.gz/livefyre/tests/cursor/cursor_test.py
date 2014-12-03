import unittest

from livefyre import Livefyre
from livefyre.tests import LfTest
from livefyre.src.cursor.factory import CursorFactory
from livefyre.src.cursor import TimelineCursor
from livefyre.src.cursor.model import CursorData
import datetime
from livefyre.src.utils import pyver


class TimelineCursorTestCase(LfTest, unittest.TestCase):
    def test_build_cursor(self):
        network = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY)
        
        date = datetime.datetime.now()
        
        cursor = TimelineCursor(network, CursorData("resource", 50, date))
        self.assertTrue(cursor)
        
        cursor.data.set_cursor_time(date)
        self.assertTrue(cursor.data.cursor_time)
        
        if pyver < 2.7:
            pass
        elif pyver < 3.0:
            with self.assertRaisesRegexp(AssertionError, 'resource is missing'):
                TimelineCursor.init(network, None, 50, datetime.datetime.now())
            with self.assertRaisesRegexp(AssertionError, 'limit is missing'):
                TimelineCursor.init(network, 'resource', None, datetime.datetime.now())
            with self.assertRaisesRegexp(AssertionError, 'cursor_time is missing'):
                TimelineCursor.init(network, 'resource', 50, None)
        else:
            with self.assertRaisesRegex(AssertionError, 'resource is missing'):
                TimelineCursor.init(network, None, 50, datetime.datetime.now())
            with self.assertRaisesRegex(AssertionError, 'limit is missing'):
                TimelineCursor.init(network, 'resource', None, datetime.datetime.now())
            with self.assertRaisesRegex(AssertionError, 'cursor_time is missing'):
                TimelineCursor.init(network, 'resource', 50, None)
        
    def test_api_calls(self):
        network = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY)
        cursor = CursorFactory.get_personal_stream_cursor(network, self.USER_ID)
         
        cursor.next_items()
        json = cursor.previous_items()
        self.assertTrue(json)

        
        
if __name__ == '__main__':
    unittest.main()