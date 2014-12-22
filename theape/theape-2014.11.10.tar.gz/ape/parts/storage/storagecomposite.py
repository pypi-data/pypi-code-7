
# this package 
from ape import BaseClass
from ape import ApeError


def check_opened(method):
    """
    A decorator to raise an ApeError if the storages aren't opened

    :param:

     - `method` : a method to call if the open_storages is not None

    :raise: ApeError if open_storages is None
    """
    def wrapped(self, *args, **kwargs):
        if self.open_storages is None:
            raise ApeError("storages must be opened before use")
        return method(self, *args, **kwargs)
    return wrapped            


class StorageComposite(BaseClass):
    """
    A composite for storages
    """
    def __init__(self):
        self._storages = None
        self.open_storages = None
        return

    @property
    def storages(self):
        """
        A list of storage objects
        """
        if self._storages is None:
            self._storages = []
        return self._storages

    def add(self, storage):
        """
        Adds the storage to the list of storages

        :param:

         - `storage`: a configured storage
        """
        if storage not in self.storages:         
            self.storages.append(storage)
        return

    def remove(self, storage):
        """
        removes the storage from self.storages

        :param:

         - `storage`: The object instance to remove
        """
        try:
            self.storages.remove(storage)
        except ValueError as error:
            self.log_error(error)
        return

    @check_opened
    def write(self, line):
        """
        Writes the line to storage

        :param:

         - `line`: a string to write to storage

        :raise: ApeError if storages not opened
        """
        for storage in self.open_storages:
            storage.write(line)
        return

    @check_opened
    def writelines(self, lines):
        """
        writes lines to opened_storages

        :param:

         - `lines`: collection of lines to send to storage

        :raise: ApeError if storages not opened
        """
        for storage in self.open_storages:
            storage.writelines(lines)
        return

    def open(self, name):
        """
        opens all the storages with `name` and puts opened storage in opened_storage

        :param:

         - `name`: name to give opened file
        """
        self.open_storages = [storage.open(name) for storage in self.storages]
        return

    def close(self):
        """
        Closes any opened storages, sets open_storages to None
        """
        if self.open_storages is not None:
            for storage in self.open_storages:
                storage.close()
            self.open_storages = None
        return
