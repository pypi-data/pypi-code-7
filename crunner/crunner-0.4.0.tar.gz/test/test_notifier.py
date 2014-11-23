# -*- coding: utf-8 -*-
import unittest

from mock import patch, Mock, call
from crunner.notifier import Notifier


def side_effect(*args, **kwargs):
    return '/tmp/' + args[1]


@patch('subprocess.Popen')
@patch('pkg_resources.resource_filename', Mock(side_effect=side_effect))
class TestNotifier(unittest.TestCase):
    def test__send_ok__call_notifier_with_correct_image(self, popen_mock):
        expected_call = '"/tmp/notifier" -i "/tmp/images/ok.png" --verbose --message "test_project"'
        notifier = Notifier('/tmp/notifier', '--message', '-i', '--verbose')
        notifier.send_ok('test_project')
        popen_mock.assert_has_calls(call(expected_call, shell=True))

    def test__send_ok__call_notifier_without_image(self, popen_mock):
        expected_call = '"/tmp/notifier" --verbose --message "test_project"'
        notifier = Notifier('/tmp/notifier', '--message', add_args='--verbose')
        notifier.send_ok('test_project')
        popen_mock.assert_has_calls(call(expected_call, shell=True))

    def test__send_nok__call_notifier_with_correct_image(self, popen_mock):
        expected_call = '"/tmp/notifier" -i "/tmp/images/nok.png" --verbose --message "test_project"'
        notifier = Notifier('/tmp/notifier', '--message', '-i', '--verbose')
        notifier.send_nok('test_project')
        popen_mock.assert_has_calls(call(expected_call, shell=True))

    def test__send_nok__call_notifier_without_image(self, popen_mock):
        expected_call = '"/tmp/notifier" --verbose --message "test_project"'
        notifier = Notifier('/tmp/notifier', '--message', add_args='--verbose')
        notifier.send_nok('test_project')
        popen_mock.assert_has_calls(call(expected_call, shell=True))


if __name__ == '__main__':
    unittest.main()
