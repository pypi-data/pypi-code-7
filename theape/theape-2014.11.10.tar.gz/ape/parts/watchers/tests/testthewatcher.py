
# python standard library
import unittest
import threading

# third party
from mock import MagicMock

# this package
from ape.parts.watchers.thewatcher import TheWatcher
from ape.parts.wifi.iwconfig import IwconfigQuery
from ape import ApeError


class TestThewatcher(unittest.TestCase):
    def setUp(self):
        self.connection = MagicMock()
        spec = IwconfigQuery(connection=self.connection)
        self.query = MagicMock(spec=spec)
        self.storage = MagicMock()
        self.fields = 'mode frequency missed_beacons'.split()
        self.header = ','.join(['timestamp'] + self.fields)

        self.watcher = TheWatcher(query=self.query,
                                   storage=self.storage,
                                   fields=self.fields)
        return

    def test_constructor(self):
        """
        Does it build correctly?
        """
        self.assertEqual(self.query, self.watcher.query)
        self.assertEqual(self.storage, self.watcher.storage)
        self.assertEqual(self.fields, self.watcher.fields)

        # defaults
        self.assertFalse(self.watcher.stopped)
        self.assertTrue(self.watcher.use_header)
        self.assertEqual(1, self.watcher.interval)
        self.assertEqual(',', self.watcher.separator)
        return

    def test_thread(self):
        """
        Does it treate a thread with run_thread as the target?
        """
        self.assertIsInstance(self.watcher.thread, threading.Thread)
        self.assertTrue(self.watcher.thread.daemon)
        self.assertEqual(self.watcher.thread._Thread__target, self.watcher.run_thread)
        return

    def test_call(self):
        """
        Does __call__ start the thread?
        """
        thread = MagicMock()
        self.watcher._thread = thread
        self.watcher()
        thread.start.assert_called_with()
        self.assertEqual('TheWatcher', thread.name)
        return

    def test_header(self):
        """
        Does it create a header from the fields?
        """
        self.assertEqual(self.watcher.header, self.header)
        return

    def test_run(self):
        """
        Does it run the watcher?
        """
        pass

    def test_check_rep(self):
        """
        Does it check the fields
        """
        self.watcher.check_rep()
        self.watcher.fields.append('cow')

        with self.assertRaises(ApeError):
            self.watcher.check_rep()
        return

    def test_stop(self):
        """
        Does it set stopped to true?
        """
        self.watcher.stop()
        self.assertTrue(self.watcher.stopped)
        return

    def test_timer(self):
        """
        Does it build the event timer correctly?
        """
        self.watcher.interval = 4
        self.assertEqual(self.watcher.timer.seconds, 4)
        return

    def test_close(self):
        """
        Does it stop the thread and close the storage?
        """
        self.watcher.stopped = False
        self.watcher.close()
        self.assertTrue(self.watcher.stopped)
        self.storage.close.assert_called_with()
        return
# end TestThewatcher
