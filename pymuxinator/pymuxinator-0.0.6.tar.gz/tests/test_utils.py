import mock

from pymuxinator import utils
from unittest import TestCase


class TestShellEscape(TestCase):
    def test_normal_string(self):
        self.assertEqual(utils.shell_escape('foo'), 'foo')

    def test_escape(self):
        self.assertEqual(utils.shell_escape('"foo"'), '\'"foo"\'')


class TestExpandPath(TestCase):
    @mock.patch('os.path.expanduser', return_value='foo')
    def test_user_path(self, mock_expanduser):
        self.assertEqual(utils.expand_path('~/foo'), 'foo')

    def test_normal_path(self):
        self.assertEqual(utils.expand_path('/home//dir/./foo'), '/home/dir/foo')


class TestExecuteCmd(TestCase):
    def test_execute(self):
        self.assertEqual(utils.execute_cmd('echo "HEY"'), 'HEY\n')
