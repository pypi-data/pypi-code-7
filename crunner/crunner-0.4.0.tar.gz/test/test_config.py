# -*- coding: utf-8 -*-
import copy
import unittest

from mock import patch, Mock, mock_open
from crunner.config import ConfigLoader


CONFIG_DATA = {
    'main': {
        'run_on_start': True,
        'delay': 5
    },
    'notifier': {
        'cmd': '/tmp/notify-send',
        'img_arg': '-i',
        'msg_arg': '-m',
        'add_args': '--hint=int:transient:1'
    },
    'tester': {
        'cmd': '/tmp/py.test',
        'args': '-s',
    },
    'projects': {
        'A': {
            'active': True,
            'test_path': '/tmp',
            'project_path': '/tmp',
            'watching_types': ['.*.py']
        }
    }
}


class TestHelper(unittest.TestCase):
    def _check_if_exit(self, config, fake_loads):
        fake_loads.return_value = config
        self.assertRaises(SystemExit, ConfigLoader().load)


@patch('crunner.config.log', Mock())
class TestConfig(TestHelper):
    @patch('__builtin__.open', mock_open())
    @patch('crunner.config.json.loads')
    @patch('crunner.config.os.path.exists', Mock(return_value=True))
    def test__load__returns_notify_and_pytest_path_and_projects(self, fake_loads):
        fake_loads.return_value = CONFIG_DATA
        main, notifier, pytest, projects = ConfigLoader().load()
        self.assertEqual(notifier['cmd'], '/tmp/notify-send')
        self.assertEqual(notifier['msg_arg'], '-m')
        self.assertEqual(notifier['img_arg'], '-i')
        self.assertEqual(notifier['add_args'], '--hint=int:transient:1')
        self.assertEqual(pytest['cmd'], '/tmp/py.test')
        self.assertEqual(pytest['args'], '-s')
        self.assertIn('A', projects)
        self.assertEqual(projects['A']['active'], True)
        self.assertEqual(projects['A']['test_path'], '/tmp')
        self.assertEqual(projects['A']['project_path'], '/tmp')
        self.assertEqual(projects['A']['watching_types'], ['.*.py'])
        self.assertEqual(main['run_on_start'], True)
        self.assertEqual(main['delay'], 5)

    @patch('crunner.config.os.path.exists')
    def test__load__exits_if_file_does_not_exist(self, exists_mock):
        self._check_if_exit(False, exists_mock)

    @patch('__builtin__.open', mock_open())
    @patch('crunner.config.json.loads')
    @patch('crunner.config.os.path.exists', Mock(return_value=True))
    def test__load__exits_if_json_format_is_not_correct(self, fake_loads):
        fake_loads.side_effect = ValueError("Wrong syntax")
        self.assertRaises(SystemExit, ConfigLoader().load)

    @patch('__builtin__.open', mock_open())
    @patch('crunner.config.json.loads')
    @patch('crunner.config.os.path.exists', Mock(return_value=True))
    def test__load__exits_if_notifier_does_not_exist(self, fake_loads):
        config = copy.deepcopy(CONFIG_DATA)
        del config['notifier']
        self._check_if_exit(config, fake_loads)

    @patch('__builtin__.open', mock_open())
    @patch('crunner.config.json.loads')
    @patch('crunner.config.os.path.exists', Mock(return_value=True))
    def test__load__exits_if_notifier_does_not_exist(self, fake_loads):
        config = copy.deepcopy(CONFIG_DATA)
        del config['tester']
        self._check_if_exit(config, fake_loads)

    @patch('__builtin__.open', mock_open())
    @patch('crunner.config.json.loads')
    @patch('crunner.config.os.path.exists', Mock(return_value=True))
    def test__load__exits_if_notifier_subkey_does_not_exist(self, fake_loads):
        config = copy.deepcopy(CONFIG_DATA)
        del config['notifier']['cmd']
        self._check_if_exit(config, fake_loads)

    @patch('__builtin__.open', mock_open())
    @patch('crunner.config.json.loads')
    @patch('crunner.config.os.path.exists', Mock(return_value=True))
    def test__load__exits_if_tester_subkey_does_not_exist(self, fake_loads):
        config = copy.deepcopy(CONFIG_DATA)
        del config['tester']['cmd']
        self._check_if_exit(config, fake_loads)

    @patch('__builtin__.open', mock_open())
    @patch('crunner.config.json.loads')
    @patch('crunner.config.os.path.exists', Mock(return_value=True))
    def test__load__exits_if_project_subkey_does_not_exist(self, fake_loads):
        config = copy.deepcopy(CONFIG_DATA)
        del config['projects']['A']['active']
        self._check_if_exit(config, fake_loads)


if __name__ == '__main__':
    unittest.main()
