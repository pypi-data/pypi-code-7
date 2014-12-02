from django.test import TestCase
from mock import Mock, ANY, patch, MagicMock
from six.moves import reload_module

from smarttest.compat import override_settings

import care.models
from care.compat import CursorWrapper
from care.models import request_data, AnnotatingCursorWrapper


class AnnotatingCursorWrapperExecuteTest(TestCase):

    def test_should_annotate_execute(self):
        cursor = Mock()
        db = MagicMock()
        db.is_managed.side_effect = [False]
        db.wrap_database_errors.__exit__.side_effect = [True]
        wrapped_cursor = CursorWrapper(cursor, db)
        cursor_wrapper = AnnotatingCursorWrapper(wrapped_cursor)
        test_sql = 'select 1;'
        request_data.path = 'test_path'
        request_data.view = 'test_view'

        cursor_wrapper.execute(test_sql)

        cursor.execute.assert_called_once_with(test_sql + ' -- path: test_path | view: test_view', ANY)


class AnnotatingCursorWrapperExecuteManyTest(TestCase):

    def test_should_annotate_executemany(self):
        cursor = Mock()
        db = MagicMock()
        db.is_managed.side_effect = [False]
        db.wrap_database_errors.__exit__.side_effect = [True]
        wrapped_cursor = CursorWrapper(cursor, db)
        cursor_wrapper = AnnotatingCursorWrapper(wrapped_cursor)
        test_sql = 'select 1;'
        request_data.path = 'test_path'
        request_data.view = 'test_view'

        cursor_wrapper.executemany(test_sql, [])

        cursor.executemany.assert_called_once_with(test_sql + ' -- path: test_path | view: test_view', ANY)


class AnnotatingCursorWrapperCallProcTest(TestCase):

    def test_should_not_annotate_call_proc(self):
        cursor = Mock()
        db = MagicMock()
        db.is_managed.side_effect = [False]
        db.wrap_database_errors.__exit__.side_effect = [True]
        wrapped_cursor = CursorWrapper(cursor, db)
        cursor_wrapper = AnnotatingCursorWrapper(wrapped_cursor)
        test_sql = 'select 1;'
        request_data.path = 'test_path'
        request_data.view = 'test_view'

        cursor_wrapper.callproc(test_sql, [])

        cursor.callproc.assert_called_once_with(test_sql, ANY)


class AnnotatingCursorWrapperTest(TestCase):

    def test_should_annotate_executemany(self):
        with override_settings(MIDDLEWARE_CLASSES='care.middleware.AnnotateSQLMiddleware'):
            reload_module(care.models)
            with patch('django.db.backends.sqlite3.base.SQLiteCursorWrapper') as SQLiteCursorWrapper:
                from care.models import request_data
                request_data.path = 'test_path'
                request_data.view = 'test_view'
                from django.db import connection
                test_sql = 'select 1;'
                connection.cursor().execute(test_sql)

                SQLiteCursorWrapper().execute.assert_called_once_with(test_sql + ' -- path: test_path | view: test_view', ANY)
        reload_module(care.models)
