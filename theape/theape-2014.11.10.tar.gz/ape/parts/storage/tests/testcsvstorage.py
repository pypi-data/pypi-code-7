
# python standard library
import unittest

# third-party
try:
    from mock import MagicMock, mock_open, patch, call
except ImportError:
    pass    

# the ape
from ape.parts.storage.csvstorage import CsvDictStorage
from ape.parts.storage.filestorage import FileStorage
from ape import ApeError


class TestCsvStorage(unittest.TestCase):
    def setUp(self):
        #self.mocked_file = mock_open()
        self.patcher = patch('__builtin__.open')
        self.mocked_file = self.patcher.start()
        self.path = 'folder'
        self.headers = "able baker charley".split()
        self.path = 'cow'
        self.file_storage = FileStorage(path=self.path)
        self.storage = CsvDictStorage(storage=self.file_storage,
                                      headers=self.headers)
        return

    def tearDown(self):
        self.patcher.stop()
        return

    def test_constructor(self):
        """
        Does it take the expected fields?
        """
        storage = CsvDictStorage(path=self.path, headers=self.headers,
                                 storage=self.file_storage)        
        self.assertEqual(self.path, storage.path)
        self.assertEqual(self.headers, storage.headers)
        self.assertEqual(self.file_storage, storage.storage)
        return

    def test_path_only(self):
        """
        Does it create the storage if only the path is given?
        """
        file_storage = MagicMock()
        file_mock = MagicMock()
        file_storage.return_value = file_mock

        storage = CsvDictStorage(path=self.path, headers=self.headers)
        with patch('ape.parts.storage.filestorage.FileStorage', file_storage):
            opened_storage = storage.storage
            self.assertEqual(opened_storage, file_mock)
            file_storage.assert_called_with(path=self.path)
        return

    def test_writer(self):
        """
        Does it create a new DictWriter if the file-storage allows it?
        """
        # should crash if no file was opened
        with self.assertRaises(ApeError):
            writer = self.storage.writer
        dict_writer = MagicMock()
        dict_writer_instance = MagicMock()
        dict_writer.return_value = dict_writer_instance

        # should work once the file is opened
        with patch('csv.DictWriter', dict_writer):
            self.storage.storage = self.storage.storage.open('test.csv')
            writer = self.storage.writer
            self.assertEqual(writer, dict_writer_instance)
            writer.writeheader.assert_called_with()
        return

    def test_bad_constructor(self):
        """
        Does it raise an error if neither path nor storage are given?
        """
        with self.assertRaises(ApeError):
            CsvDictStorage(headers=self.headers)

        with self.assertRaises(TypeError):
            # headers are required too
            CsvDictStorage(path=self.path)
            
        with self.assertRaises(TypeError):            
            CsvDictStorage(storage = self.file_storage)

        with self.assertRaises(TypeError):
            CsvDictStorage()
        return

    def test_writerow(self):
        """
        Does it write the row?
        """
        data = dict(zip(self.headers, ('1', '2', '3')))
        writer = MagicMock()
        self.storage._writer = writer
        self.storage.writerow(rowdict=data)
        writer.writerow.assert_called_with(rowdict=data)

        # keys don't match header, should raise ValueError
        writer.writerow.side_effect = ValueError("argh")
        with self.assertRaises(ApeError):
            self.storage.writerow(data)

        # keys don't match header, data wasn't strings
        writer.writerow.side_effect = TypeError("double bad")
        with self.assertRaises(ApeError):
            self.storage.writerow(data)

        # something other than a dict was given to the method
        with self.assertRaises(ApeError):
            self.storage.writerow(1)
        return

    def test_writerows(self):
        """
        Does it write each dict in the list?
        """
        writer = MagicMock()
        data = 'fake'
        self.storage._writer = writer
        self.storage.writerows(data)

        # CsvDictStorage uses its writerow method instead of writerows
        # so the errors are tested in test_writerow
        calls = [call(rowdict=letter) for letter in data]
        self.assertEqual(calls, writer.writerow.mock_calls)
        return

    def test_open(self):
        """
        Does it open a file with the given filename?
        """
        name = 'aoeu'
        dict_writer = MagicMock()
        dict_writer_instance = MagicMock()
        storage = MagicMock()
        dict_writer.return_value = dict_writer_instance
        self.file_storage.open = MagicMock()
        opened = MagicMock()
        self.file_storage.open.return_value = opened
        
        with patch('csv.DictWriter', dict_writer):
            # the call to `open`
            writer = self.storage.open(name)

            # did it open a file using the filename?
            self.file_storage.open.assert_called_with(name)

            # Did it create and store a DictWriter?
            self.assertEqual(writer.writer, dict_writer_instance)

            # Did it create the DictWriter using the opened file and headers?
            dict_writer.assert_called_with(opened,
                                           self.headers)

            # Did it write the header to the file?
            dict_writer_instance.writeheader.assert_called_with()

            # did it return a copy of itself?
            self.assertIsInstance(writer, CsvDictStorage)
            self.assertNotEqual(writer, self.storage)
        return        
