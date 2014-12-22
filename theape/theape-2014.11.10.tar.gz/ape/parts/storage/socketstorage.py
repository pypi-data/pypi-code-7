
# python standard library
import os
import socket

# this package
from base_storage import BaseStorage

#from ape import BaseClass
from ape import ApeError
from ape.infrastructure.code_graphs import module_diagram, class_diagram


NEWLINE = '\n'
SPACE = ' '
EOF = ''
IN_PWEAVE = __name__ == '__builtin__'
TIMED_OUT = 'timed out'


class SocketStorage(BaseStorage):
    """
    A class to store data to a file
    """
    def __init__(self, file_object):
        """
        SocketStorage constructor

        :param:

         - `file_object`: opened file-like socket-based object
        """
        super(SocketStorage, self).__init__()
        self._file = file_object
        self.closed = False
        return

    @property
    def file(self):
        """
        :return: opened file-like object
        """
        return self._file

    def readline(self):
        """
        Calls a single read-line returns 'timed out' if socket.timeout
        """
        try:
            return self.file.readline()
        except socket.timeout:
            self.logger.debug('socket timedout')
            return TIMED_OUT
        
    
    def read(self):
        """
        reads all the output and returns as a single string

        :raise: ApeError if socket times-out
        """
        try:        
            return self.file.read()
        except socket.timeout as error:
            self.logger.debug(TIMED_OUT)
            raise ApeError('Socket Timed Out')
        return

    def readlines(self):
        """
        reads all the output and returns a list of lines

        :raise: ApeError if the socket times out
        """
        try:
            return self.file.readlines()
        except socket.timeout as error:
            self.logger.debug(TIMED_OUT)
            raise ApeError("Socket Timed Out")

    def write(self, text):
        """
        write text to a file

        :param:

         - `text`: text to write to the file

        :raise: ApeError on socket.error
        """
        super(SocketStorage, self).write(text, socket.error)
        return

    def writelines(self, texts):
        """
        write lines to a file (does not add newline character to end of lines)

        :param:

         - `texts`: iterable collection of strings to write to the file

        :raise: ApeError on socket.error (socket closed)
        """
        super(SocketStorage, self).writelines(texts, socket.error)
        

    def __iter__(self):
        """
        Traverses the file

        :yield: next line in the file (or 'timed out' if it times-out)
        """
        line = None
        while line != EOF:
            try:
                line =  self.file.readline()
                yield line
            except socket.timeout:
                self.logger.debug('socket timed out')
                yield TIMED_OUT
        return
    


if IN_PWEAVE:
    this_file = os.path.join(os.getcwd(), 'socketstorage.py')
    module_diagram_file = module_diagram(module=this_file, project='socketstorage')
    print ".. image:: {0}".format(module_diagram_file)

