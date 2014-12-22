
# python standard library
import sys

# this package
from base_storage import BaseStorage


class ScreenStorage(BaseStorage):
    """
    An adapter for stdout so it can be used in the StorageComposite
    """
    def __init__(self):
        super(ScreenStorage, self).__init__()
        self._file = None
        return

    @property
    def file(self):
        """
        sys.stdout
        """
        if self._file is None:
            self._file = sys.stdout
        return self._file

    def close(self):
        """
        Does nothing
        """
        return

    def open(self, name):
        """
        Does Nothing
        """
        return
