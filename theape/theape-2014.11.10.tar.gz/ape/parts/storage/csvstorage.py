
# python standard library
import copy
import csv
from types import DictType

# the ape
from ape import BaseClass
from ape import ApeError
import ape.parts.storage.filestorage


class CsvDictStorage(BaseClass):
    """
    A storage that writes to csv files
    """
    def __init__(self, headers,
                 path=None, storage=None):
        """
        CsvDictStorage constructor

        :param:

         - `path`: path to folder to store output-file in 
         - `storage`: file-like object to use instead of creating one from 'path'
         - `headers`: list of column headers in order required
        :raises: ApeError if neither `path` nor `storage` given
        """
        super(CsvDictStorage, self).__init__()
        self.path = path
        self.headers = headers
        self._storage = storage
        self._writer = None

        if not any((self.path, self._storage)):
            raise ApeError("Path or storage needed.")
        return

    @property
    def storage(self):
        """
        A file-storage created from the path (unless passed into constructor)

        :return: FileStorage        
        """
        if self._storage is None:
            self._storage = ape.parts.storage.filestorage.FileStorage(path=self.path)
        return self._storage

    @storage.setter
    def storage(self, new_storage):
        """
        Sets the storage to what's passed in

        :param:

         - `new_storage`: Storage instance to give the DictWriter
        """
        self._storage = new_storage
        return

    @property
    def writer(self):
        """
        DictWriter instance (creates it if not set)

        :postcondition: if dictwriter created, header written to file
        :raise: ApeError if not set and storage not writeable
        """
        if self._writer is None:
            if self.storage.closed or not self.storage.mode.startswith('w'):
                raise ApeError("FileStorage not open")
            self._writer = csv.DictWriter(self.storage,
                                          self.headers)
            # assume this is a new file
            self._writer.writeheader()
        return self._writer
            

    def open(self, filename):
        """
        Opens the filename as a DictWriter

        :param:

         - `filename`: the name of the file to open

        :postcondition: header written to file
        :return: copy of self with open DictWriter as `writer`
        """
        new_writer = copy.copy(self)
        open_file = self.storage.open(filename)
        # DictWriter doesn't like keyword arguments
        new_writer._writer = csv.DictWriter(open_file,
                                           self.headers)
        new_writer.writer.writeheader()
        return new_writer

    def writerow(self, rowdict):
        """
        Writes the row to storage

        :param:

         - `rowdict`: dict whose keys match the headers

        :raise: ApeError if keys don't match header or invalid data was passed in.
        """
        try:
            self.writer.writerow(rowdict=rowdict)
        except ValueError as error:
            self.logger.error(error)
            raise ApeError("rowdict keys invalid")
        except TypeError as error:
            if type(rowdict) is not DictType:
                raise ApeError("rowdict not `header:data` dict  ({0})".format(rowdict))
            self.logger.debug(error)
            self.logger.error(("key in ({0}) not in header ({1}) "
                              "and non-string in data ({2})").format(rowdict.keys(),
                                                                    self.headers,
                                                                    rowdict.values()))
            raise ApeError("rowdict keys and values invalid")
        return
    
    def writerows(self, rowdicts):
        """
        Writes each dictionary in rowdicts to the csv

        :param:

         - `rowdicts`: iterable collection of dictionaries

        :raise: ApeError (see writerow)
        """
        for rowdict in rowdicts:
            self.writerow(rowdict)
        return


if __name__ == "__main__":
    #import pudb; pudb.set_trace()
    #from mock import mock_open, patch
    #mocked_file = mock_open()
    #headers = 'able baker charley'.split()
    #with patch('__builtin__.open', mocked_file, create=True):
    #    with open('test', 'w') as m:
    #        writer = csv.DictWriter(m,
    #                                headers)
    headers = 'able baker charley'.split()
    raw_data = """1 2 3
4 5 6
7 8 9
10 11 12"""
    raw_rows = raw_data.split('\n')
    rows = list(dict(zip(headers, row.split())) for row in raw_rows)
    with ape.parts.storage.filestorage.FileStorage(path='tests', name='test.csv', overwrite=True) as testfile:
        writer = CsvDictStorage(headers=headers,
                                storage=testfile)
        writer.writerows(rows)

    with open('tests/test.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        assert reader.fieldnames == headers
        for index, row in enumerate(reader):
            for column in headers:
                assert rows[index][column] == row[column]
