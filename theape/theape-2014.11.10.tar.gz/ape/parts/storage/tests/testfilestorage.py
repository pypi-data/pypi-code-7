
# python standard library
import unittest
import shutil
import os

# third party
try:
    from mock import MagicMock, mock_open, patch
except ImportError:
    pass    

# this package
from ape.parts.storage.filestorage import FileStorage, AMBIGUOUS
from ape.commoncode.errors import ApeError


PATH = 'ape/call'
class TestFileStorage(unittest.TestCase):
    def setUp(self):
        self.storage = FileStorage('test')
        self.mock_file = MagicMock()
        return

    def test_constructor(self):
        """
        Does it set up the name and the BaseStorage parent?
        """
        storage = FileStorage(PATH)
        self.assertEqual(PATH, storage.path)
        return
        
    def test_write(self):
        self.storage._file = self.mock_file
        self.storage.write('alpha')
        self.mock_file.write.assert_called_with('alpha')
        
    def test_write_error(self):
        storage = FileStorage(PATH)
        self.assertRaises(ApeError, storage.write, ('',))
        return

    def test_writeline(self):
        self.storage._file = self.mock_file
        self.storage.writeline('beta')
        self.mock_file.write.assert_called_with('beta\n')
        return

    def test_writelines(self):
        text = 'gamma delta sigma rho'.split()
        self.storage._file = self.mock_file
        self.storage.writelines(text)
        self.mock_file.writelines.assert_called_with(text)
        return

    def test_writeable(self):
        mocked = mock_open()
        name = 'ummagumma.txt'
        full_name = 'test/' + name
        storage = FileStorage('test/')
        with patch('__builtin__.open', mocked):
            self.assertFalse(storage.writeable)
            opened = storage.open(name)
            self.assertTrue(opened.writeable)
            opened.close()
            self.assertFalse(opened.writeable)
        return
    
    def test_close(self):
        mock_file = MagicMock()
        self.storage._file = mock_file
        self.storage.closed = False
        self.storage.close()
        mock_file.close.assert_called_with()
        self.assertTrue(self.storage.closed)
        return
    
    def tearDown(self):
        if os.path.isdir(PATH):
            shutil.rmtree(PATH)
        return        


PATH = 'ape/call'
class TestFileStorageOpen(unittest.TestCase):
    def setUp(self):
        self.storage = FileStorage('test')
        self.mock_file = MagicMock()
        return

    def test_open(self):
        """
        Does it open the file normally if the file doesn't already exist?
        """
        mocked = mock_open()
        name = 'ummagumma.txt'
        full_name = 'test/' + name
        storage = FileStorage('test/')
        with patch('__builtin__.open', mocked):
            self.assertTrue(storage.closed)
            opened = storage.open(name)
            self.assertEqual(full_name, opened.name)
            mocked.assert_called_with(full_name, 'w')
            self.assertFalse(opened.closed)
            self.assertEqual(opened.mode, 'w')

            # test append
            opened = storage.open(name, mode='a')
            mocked.assert_called_with(full_name, 'a')

            #test over-write
            opened = storage.open(name, overwrite=True)
            mocked.assert_called_with(full_name, 'w')

            # test append and over-write
            opened = storage.open(name, overwrite=True, mode='a')
            mocked.assert_called_with(full_name, 'a')
        return

    def test_open_file_exists(self):
        """
        Does it mangle the file-names at the right times?
        """
        mocked = mock_open()
        name = 'ummagumma.txt'
        
        storage = FileStorage('test/')
        mock_os_listdir = MagicMock()
        mock_os_path_exists = MagicMock()
        mock_os_path_join = MagicMock()

        mock_open_path_exists = True
        mock_os_listdir.return_value = ['ummagumma.txt']
        def join(path, name):
            return path + name

        mock_os_path_join.side_effect = join

        mangled = 'test/ummagumma_0001.txt'
        un_mangled = 'test/' + name
        
        with patch('__builtin__.open', mocked):
            with patch('os.path.join', mock_os_path_join):
                with patch('os.path.exists', mock_os_path_exists):
                    with patch('os.listdir', mock_os_listdir):
                        # default behavior
                        opened = storage.open(name)
                        mocked.assert_called_with(mangled, 'w')

                        # append, don't clobber
                        opened = storage.open(name, mode='a')
                        mocked.assert_called_with(un_mangled, 'a')

                        # overwrite, don't clobber
                        opened = storage.open(name, overwrite=True)
                        mocked.assert_called_with(un_mangled, 'w')

                        # append, give warning
                        storage._logger = MagicMock()
                        opened = storage.open(name,
                                              overwrite=True,
                                              mode='a')
                        mocked.assert_called_with(un_mangled, 'a')
                        storage._logger.warning.assert_called_with(AMBIGUOUS)
        return
# end class TestFileStorageOpen


class TestFileStorageWith(unittest.TestCase):
    def setUp(self):
        self.storage = FileStorage('test')
        self.mock_file = MagicMock()
        return

    def test_with(self):
        """
        Does it work with the with statement?
        """
        mocked = mock_open()
        open_file = MagicMock(name='open_file')
        mocked.return_value = open_file
        name = 'ummagumma.txt'
        full_name = 'test/' + name
        #storage = FileStorage('test/')
        with patch('__builtin__.open', mocked):
            with FileStorage(path='test', name=name) as new_storage:
                mocked.assert_called_with(full_name, 'w')
                self.assertEqual(open_file, new_storage.file)
                self.assertFalse(new_storage.closed)
                self.assertIsNotNone(new_storage.file)
        self.assertIsNotNone(new_storage.file)
        new_storage.file.close.assert_called_with()
        return
        
                
