
# python standard library
import unittest

# third-party
try:
    from mock import MagicMock
except ImportError:
    pass

# this package
from ape.parts.storage.storagecomposite import StorageComposite
from ape import ApeError


class TestStorageComposite(unittest.TestCase):
    def setUp(self):
        self.composite = StorageComposite()
        self.opened = MagicMock()
        self.storage = MagicMock()
        self.open = MagicMock()

        self.storage.open = self.open
        self.open.return_value = self.opened
        return

    def test_constructor(self):
        self.assertIsNone(self.composite.open_storages)
        return

    def test_add(self):
        self.composite.add(self.storage)
        self.assertIn(self.storage, self.composite.storages)
        return

    def test_remove(self):
        self.composite.add(self.storage)
        self.assertIn(self.storage, self.composite.storages)
        self.composite.remove(self.storage)
        self.assertNotIn(self.storage, self.composite.storages)

    def test_open(self):
        self.composite.add(self.storage)
        self.composite.open('ummagumma')
        self.open.assert_called_with('ummagumma')

    def test_write(self):
        self.assertRaises(ApeError, self.composite.write, ('test',))
        self.composite.add(self.storage)
        self.composite.open('ape.csv')
        self.composite.write('aoeu')
        self.assertIn(self.opened, self.composite.open_storages)

        self.opened.write.assert_called_with('aoeu')
        return

    def test_writelines(self):
        self.composite.add(self.storage)
        lines = 'a b c d'.split()
        self.assertRaises(ApeError, self.composite.writelines, (lines,))
        self.composite.open('aoeu')
        self.composite.writelines(lines)
        self.opened.writelines.assert_called_with(lines)

    def test_close(self):
        self.composite.add(self.storage)
        self.composite.open('taco')
        self.composite.close()
        self.opened.close.assert_called_with()
        self.assertIsNone(self.composite.open_storages)
        self.composite.close()
        return                       
