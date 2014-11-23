# -*- coding: utf-8 -*-
import os
import unittest

from mock import patch, call, Mock
from crunner import runner


@patch('crunner.runner.log', Mock())
class TestRunner(unittest.TestCase):
    def setUp(self):
        self.notifier = Mock()
        self.runner = runner.Runner(self.notifier, tester_cmd='/tmp/py.test', tester_args='-s')

    @patch('crunner.runner.call')
    @patch('os.path.exists', Mock(return_value=True))
    @patch('os.chdir', Mock())
    def test__test__executes_tester(self, fake_popen):
        self.runner.test(name="Project", project_path='/project', test_path='/tmp')
        fake_popen.assert_has_calls(call('cd /project; /tmp/py.test -s /tmp', shell=True))

    @patch('crunner.runner.call', Mock())
    @patch('os.path.exists', Mock(return_value=False))
    @patch('os.chdir', Mock())
    def test__test__calls_notifier_to_send_negative_result_if_project_path_does_not_exist(self):
        self.runner.test(name="Project", project_path='/project', test_path='/tmp')
        self.notifier.assert_has_calls(call.send_nok("Project"))

    @patch('crunner.runner.call')
    @patch('os.path.exists', Mock(return_value=True))
    @patch('os.chdir', Mock())
    def test__test__calls_notifier_to_send_positive_result(self, fake_popen):
        fake_popen.return_value = 0
        self.runner.test(name="Project", project_path='/project', test_path='/tmp')
        self.notifier.assert_has_calls(call.send_ok("Project"))

    @patch('crunner.runner.call')
    @patch('os.path.exists', Mock(return_value=True))
    @patch('os.chdir', Mock())
    def test__test__calls_notifier_to_send_negative_result(self, fake_popen):
        fake_popen.return_value = -1
        self.runner.test(name="Project", project_path='/project', test_path='/tmp')
        self.notifier.assert_has_calls(call.send_nok("Project"))


if __name__ == '__main__':
    unittest.main()
