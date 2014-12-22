
# python standard library
import unittest
import socket
import textwrap

# third-party
try:
    from mock import patch, MagicMock
except ImportError:
    pass

# this package
from ape.parts.storage.socketstorage import SocketStorage
import ape.parts.storage.socketstorage as socketstorage
from ape import ApeError


class TestSocketStorage(unittest.TestCase):
    """
    Tests the SocketStorage class
    """
    def setUp(self):
        """
        Builds the storage with a mock for the socket (channel) file
        """
        self.socket = MagicMock()
        self.storage = SocketStorage(self.socket)
        return

    def test_constructor(self):
        """
        Makes sure the signature is as expected (requires a file to be passed in)
        """
        self.assertEqual(self.storage.file, self.socket)
        with self.assertRaises(TypeError):
            SocketStorage()
        return

    def test_close(self):
        """
        Is the file closed and the 'closed' attribute set to True?
        """
        self.assertFalse(self.storage.closed)
        self.storage.close()
        self.socket.close.assert_called_with()
        self.assertTrue(self.storage.closed)
        return

    def test_read(self):
        """
        Does it call the channel's 'read' method?
        """
        output = 'a\nb\nc\n'
        reader = MagicMock()
        reader.read.return_value = output
        self.storage._file = reader
        actual = self.storage.read()
        self.assertEqual(output, actual)
        return

    def test_read_timeout(self):
        """
        Does it catch the `socket.timeout` and raise an ApeError instead?
        """
        self.socket.read.side_effect = socket.timeout
        self.assertRaises(ApeError, self.storage.read)
        return

    def test_readlines(self):
        """
        Does it call the channel's readlines method?
        """        
        expected = 'alpha bravo charley'.split() 
        output = MagicMock()
        output.readlines.return_value = expected
        self.storage._file = output
        actual = self.storage.readlines()
        self.assertEqual(actual, expected)        
        return

    def test_readlines_timeout(self):
        """
        Does it catch socket.timeout and raise an ApeError instead?
        """
        self.socket.readlines.side_effect = socket.timeout
        self.assertRaises(ApeError, self.storage.readlines)
        

    def test_readline(self):
        """
        Does it call the channel's readline method?
        """
        expected = 'some line\n'
        self.socket.readline.return_value = expected
        actual = self.storage.readline()
        self.assertEqual(actual, expected)
        return

    def test_readline_timeout(self):
        """
        Does it return a 'timed out' message on readline timeout?
        """
        self.socket.readline.side_effect = socket.timeout
        actual = self.storage.readline()
        self.assertEqual(socketstorage.TIMED_OUT, actual)

    def test_write(self):
        """
        Does it call the Channel's write method?
        """
        expected = 'now is the winter of our discontent\n'
        self.storage.write(expected)
        self.socket.write.assert_called_with(expected)
        return

    def test_write_closed(self):
        """
        Does it raise an ApeError if the socket is closed?
        """
        self.socket.write.side_effect = socket.error
        self.assertRaises(ApeError, self.storage.write, '')
        return

    def test_writeline(self):
        """
        Does writeline add a newline and write to the file?
        """
        text = "I'm enery the eighth I am"
        self.storage.writeline(text)
        self.socket.write.assert_called_with(text + socketstorage.NEWLINE)
        return

    def test_writeline_error(self):
        """
        Does it raise an ApeError on socket error?
        """
        self.socket.write.side_effect = socket.timeout
        self.assertRaises(ApeError, self.storage.writeline, '')
        return

    def test_writelines(self):
        """
        Does it call the Channel's writelines method?
        """
        text = 'a\n b\n c\n'.split()
        self.storage.writelines(text)
        self.socket.writelines.assert_called_with(text)
        return

    def test_writelines_error(self):
        """
        Does it raise an ApeError on socket.error?
        """
        self.socket.writelines.side_effect = socket.error
        self.assertRaises(ApeError, self.storage.writelines, '')
        return

    def test_iter(self):
        """
        Does it traverse the socket output?
        """
        lines = textwrap.dedent('''Now is the winter of our discontent,
        Made glorious Summer by this Son of Yorke,
        And all the clouds that lour'd upon our house,
        In the deep bosom of the ocean buried.
        ''').split('\n')
        output = lines[:]
        def readline():
            if len(output):
                return output.pop(0)
            return ''
        
        self.socket.readline.side_effect = readline
        for index, line in enumerate(self.storage):
            print index, line
            self.assertEqual(line, lines[index])
            
# end class TestSocket    
