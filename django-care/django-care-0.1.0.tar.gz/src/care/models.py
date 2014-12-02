""" Models. """
import threading

from django.conf import settings
from django.db.backends import BaseDatabaseWrapper

from care.compat import CursorWrapper

request_data = threading.local()
request_data.path = ''
request_data.view = ''


class AnnotatingCursorWrapper(CursorWrapper):

    """ Cursor wrapper appending path into sql comment.

    This wrapper appends request path and resolved view into sql comment
    in order to easier find source of query in slow log.
    Wrapper automaticaly monkey-paches BaseDatabaseWrapper
    if AnnotateSQLMiddleware is in MIDDLEWARE_CLASSES.

    .. versionadded:: 1.1
    """

    def __init__(self, cursor_wrapper):
        """ Wrap existing cursor wrapper.

        :param cursor_wrapper: CursorWrapper instance
        """
        self.wrapped = cursor_wrapper

    def execute(self, sql, params=()):
        """ Execute sql query.

        :param sql: sql query
        :param params: sql params to interpolate
        """
        path = getattr(request_data, 'path', '')
        view = getattr(request_data, 'view', '')
        sql += ' -- path: %s | view: %s' % (path.replace('%', '%%'), view.replace('%', '%%'))
        return self.wrapped.execute(sql, params)

    def executemany(self, sql, param_list):
        """ Execute sql query.

        :param sql: sql query
        :param params: sql params to interpolate
        """
        path = getattr(request_data, 'path', '')
        view = getattr(request_data, 'view', '')
        sql += ' -- path: %s | view: %s' % (path.replace('%', '%%'), view.replace('%', '%%'))
        return self.wrapped.executemany(sql, param_list)

    def __getattribute__(self, name):
        """ Proxy attributes to CursorWrapper instance. """
        if name in ['execute', 'executemany', 'wrapped']:
            return object.__getattribute__(self, name)
        return object.__getattribute__(self.wrapped, name)


if 'care.middleware.AnnotateSQLMiddleware' in settings.MIDDLEWARE_CLASSES:
    old_cursor = BaseDatabaseWrapper.cursor
    BaseDatabaseWrapper.cursor = lambda *args: AnnotatingCursorWrapper(old_cursor(*args))
