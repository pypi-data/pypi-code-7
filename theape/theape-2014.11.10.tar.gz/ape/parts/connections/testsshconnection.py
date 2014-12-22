
# python standard library
import unittest
import socket

# third-party
import paramiko
try:
    from mock import MagicMock, patch    
except ImportError:
    pass

# this package
from ape.parts.connections.sshconnection import SSHConnection
from ape.parts.connections.sshconnection import InOutError
from ape import ApeError


class TestSSHConnection(unittest.TestCase):
    """
    Tests the SSHConnection
    """
    def setUp(self):
        paramiko_patcher = patch('paramiko.SSHClient')
        self.definition = paramiko_patcher.start()
        self.client = MagicMock()
        self.stdin = MagicMock()
        self.stdout = MagicMock()
        self.stderr = MagicMock()
        self.hostname = 'snth'
        self.username = 'aoeu'
        self.password = 'zvwm'
        self.timeout = 10
        
        self.client = MagicMock()
        self.logger = MagicMock()
        self.definition.return_value = self.client
        
        self.connection = SSHConnection(hostname=self.hostname,
                                        username=self.username,
                                        password=self.password,
                                        timeout=self.timeout)
        self.connection._logger = self.logger
        self.client.exec_command.return_value = (self.stdin, self.stdout, self.stderr)
        return

    def tearDown(self):
        self.definition.stop()
        return

    def test_constructor(self):
        """
        Does the constructor's signature match what is expected?
        """
        hostname = 'aoeusnth'
        username = 'qjkzvwm'
        connection = SSHConnection(hostname=hostname,
                                   username=username)
        self.assertEqual(connection.hostname, hostname)
        self.assertEqual(connection.username, username)

        # required parameters
        self.assertRaises(TypeError, SSHConnection)

        # defaults
        self.assertEqual(None, connection.prefix)
        self.assertEqual(22, connection.port)
        self.assertIsNone(connection.password)
        self.assertFalse(connection.compress)
        self.assertIsNone(connection.key_filename)
        self.assertIsNone(connection.timeout)
        return

    def test_client(self):
        """
        Does the connection build the SSHClient as expected?
        """
        #with patch('paramiko.SSHClient', self.definition):
        sshclient = self.connection.client
        self.definition.assert_called_with()
        self.client.connect.assert_called_with(hostname=self.hostname,
                                           username=self.username,
                                           password=self.password,
                                           port=22,
                                           key_filename=None,
                                           compress=False,
                                           timeout=self.timeout)
        self.assertEqual(self.client, sshclient)
        return

    def test_bad_public_keys(self):
        """
        Does it catch the PasswordRequiredException?
        """
        self.client.connect.side_effect = paramiko.PasswordRequiredException
        self.connection._client = None
        with self.assertRaises(ApeError):
            client = self.connection.client
        return

    def test_bad_password(self):
        """
        Does it catch an incorrect password (or username)?
        """
        self.client.connect.side_effect = paramiko.AuthenticationException
        self.connection._client = None
        with self.assertRaises(ApeError):
            self.connection.client
        return

    def socket_errors(self, message):
        self.client.connect.side_effect = socket.error(message)
        self.connection._client = None
        with self.assertRaises(ApeError):
            self.connection.client
        
    def test_ip_problems(self):
        """
        Does it catch socket errors?
        """
        self.socket_errors('[Errno 113] No route to host')
        self.socket_errors('[Errno 101] Network is unreachable')
        self.socket_errors('[Errno 111] Connection refused')
        self.socket_errors('timed out')
        self.socket_errors('unknown error')
        return

    def test_sshexception(self):
        """
        Does it raise an ApeError for all paramiko-exceptions?
        """
        self.client.connect.side_effect = paramiko.SSHException
        self.connection._client = None
        with self.assertRaises(ApeError):
            self.connection.client
        return

    def test_sudo(self):
        """
        Does the connection make the proper calls to issue a sudo command?
        """

        with patch('paramiko.SSHClient', self.definition):
            command = 'alpha bravo'
            password = 'sntahoeu'
            timeout = 1
            ioe = self.connection.sudo(command=command,
                                       password=password,
                                       timeout=timeout)
        self.client.exec_command.assert_called_with('sudo {0}'.format(command), bufsize=-1,
                                                    timeout=None, get_pty=True)
        self.stdin.write.assert_called_with(password + '\n')
        self.assertEqual(ioe.input.file, self.stdin)
        self.assertEqual(ioe.output.file, self.stdout)
        self.assertEqual(ioe.error.file, self.stderr)
        return

    def test_call(self):
        """
        Does the call act the same as paramiko's exec_command?
        """
        command = 'bow down before me, the one true king'
        ioe = self.connection(command)
        self.connection.client.exec_command.assert_called_with(command, bufsize=-1,
                                                               timeout=None, get_pty=False)
        return

    def test_prefix(self):
        """
        Does it add the prefix to the command sent over the connection?
        """
        self.connection.prefix = "Aba daba daba daba daba daba dab. Said the chimpie to the monk."
        command = "What I desire is man's red fire"
        ioe = self.connection(command)
        self.connection.client.exec_command.assert_called_with("{0};{1}".format(self.connection.prefix, command), bufsize=-1,
                                                               timeout=None, get_pty=False)
        

    def test_exec_command(self):
        """
        Is this the same thing as the call?
        """
        command = "Alkohol ist nicht die Antwort, ist die Losung"
        ioe = self.connection.exec_command(command)
        self.connection.client.exec_command.assert_called_with(command, bufsize=-1,
                                                               timeout=None, get_pty=False)


    def test_getattr(self):
        """
        Does the getattr call the client correctly?
        """
        command = "Art is the supreme task and the truly metaphysical activity in this life..."
        ioe = self.connection.nietzsche(command)
        self.connection.client.exec_command.assert_called_with('nietzsche ' + command, bufsize=-1,
                                                               timeout=None, get_pty=False)
        

    def test_lock(self):
        """
        Does the connection return the same lock to all users?
        """
        lock_1 = self.connection.lock
        lock_2 = self.connection.lock
        self.assertIs(lock_1, lock_2)
        return

    def test_close(self):
        """
        Does it close the connection and re-set it to None?
        """
        self.connection.close()
        self.client.close.assert_called_with()
        self.assertIsNone(self.connection._client)
# end TestSSHConnection
