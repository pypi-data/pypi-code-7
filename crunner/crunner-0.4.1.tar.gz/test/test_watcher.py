# -*- coding: utf-8 -*-
import unittest

from mock import patch, call, Mock
from crunner.watcher import FileWatcher


class TestWatcher(unittest.TestCase):
    @patch('crunner.watcher.Observer')
    def test__start__starts_observer(self, fake):
        event = Mock()
        FileWatcher('/tmp', event).start()
        fake.assert_has_calls(call().schedule(event, '/tmp', recursive=True))
        fake.assert_has_calls(call().start())

    @patch('crunner.watcher.Observer')
    def test__stop__stops_observer(self, fake):
        event = Mock()
        file_watcher = FileWatcher('/tmp', event)
        file_watcher.start()
        file_watcher.stop()
        fake.assert_has_calls(call().stop())


if __name__ == '__main__':
    unittest.main()
