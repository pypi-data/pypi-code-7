from django.test import TestCase
from mock import Mock, MagicMock

from care.compat import CursorWrapper

try:
    from django.db.backends.util import CursorWrapper  # noqa
except ImportError:

    # For Django < 1.3

    class CursorWrapperGetAttrTest(TestCase):

        def test_should_proxy_attr(self):
            cursor = Mock()
            db = MagicMock()
            cursor_wrapper = CursorWrapper(cursor, db)

            execute = cursor_wrapper.execute

            self.assertEqual(execute, cursor.execute)

        def test_should_return_cursor_iterator(self):
            cursor = []
            db = MagicMock()
            cursor_wrapper = CursorWrapper(cursor, db)

            old_cursor = iter(cursor_wrapper)

            self.assertEqual(list(old_cursor), cursor)
