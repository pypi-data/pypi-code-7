""" Compatibility module. """
try:
    from django.db.backends.util import CursorWrapper
except ImportError:

    # Copied form Django 1.3

    class CursorWrapper(object):

        """ Adds support for CursorWrapper for Django 1.2. """

        def __init__(self, cursor, db):
            """ Create CursorWrapper. """
            self.cursor = cursor
            self.db = db

        def __getattr__(self, attr):
            """ Proxy attributes to cursor. """
            if self.db.is_managed():
                self.db.set_dirty()
            if attr in self.__dict__:
                return self.__dict__[attr]  # pragma: no cover
            else:
                return getattr(self.cursor, attr)

        def __iter__(self):
            """ Create iterator over cursor. """
            return iter(self.cursor)


__all__ = ('CursorWrapper',)
