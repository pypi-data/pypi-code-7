
# python standard library
import unittest

# third-party
try:
    from mock import patch
except ImportError:
    pass    

# this package
from ape.parts.storage.screenstorage import ScreenStorage


class TestScreenStorage(unittest.TestCase):
    def setUp(self):
        self.sys_patch = patch('sys.stdout')
        self.stdout = self.sys_patch.start()
        self.storage = ScreenStorage()        
        return

    def tearDown(self):
        self.sys_patch.stop()
        return

    def test_constructor(self):
        return

    def test_close(self):
        self.storage.close()
        self.assertFalse(self.stdout.close.called)
        return

    def test_open(self):
        self.storage.open('fake')
        self.assertFalse(self.stdout.open.called)
        return

    def test_write(self):
        self.storage.write('cow')
        self.stdout.write.assert_called_with('cow')
        return

    def test_writelines(self):
        lines = 'a b c d'.split()
        self.storage.writelines(lines)
        self.stdout.writelines.assert_called_with(lines)
        return

    def test_writeline(self):
        line = 'aoeusnth'
        self.storage.writeline(line)
        self.stdout.write.assert_called_with(line + '\n')

