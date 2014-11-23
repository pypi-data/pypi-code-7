# -*- coding: utf-8 -*-
import time
import unittest

from mock import Mock, call
from crunner.event import FileEvent


class TestFileEvent(unittest.TestCase):
    def test__on_modified__executes_runner(self):
        runner = ['Test1', Mock(), '/project', '/test1']
        event = FileEvent(exec_params=runner, delay=5)
        event.last_executed = time.time() - 5
        event.on_modified(Mock())
        runner[1].assert_has_calls(call.test('Test1', '/project', '/test1'))

    def test__run_tests__executes_runner(self):
        runner = ['Test1', Mock(), '/project', '/test1']
        event = FileEvent(exec_params=runner, delay=5)
        event.run_tests()
        runner[1].assert_has_calls(call.test('Test1', '/project', '/test1'))


if __name__ == '__main__':
    unittest.main()
