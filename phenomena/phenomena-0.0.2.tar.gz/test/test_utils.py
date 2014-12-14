from cStringIO import StringIO
import logging
import re
import sys

from phenomena.event_core import EventCore


class StdOutCapture(list):
    def __init__(self, seq=(), noop=False):
        super(StdOutCapture, self).__init__(seq)

        self._noop = noop

    def __enter__(self):
        if self._noop:
            return self

        self._original_stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._noop:
            return

        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._original_stdout


class CaptureHandler(logging.StreamHandler):
    MSG_RE = re.compile(r'(?:.* -- )(?P<Message>.*)')

    def __init__(self):
        self._stream = StringIO()

        super(CaptureHandler, self).__init__(self._stream)


    def read_logs(self):
        logs = []

        for log in self._stream.getvalue().splitlines():
            logs.append(log)

        self._stream.truncate(0)

        return logs

    def read_messages(self):
        msgs = []

        for log in self._stream.getvalue().splitlines():
            msgs.append(self.MSG_RE.match(log).group('Message'))

        self._stream.truncate(0)

        return msgs


def create_capture_log(log_level=logging.ERROR):
    capture_handle = CaptureHandler()
    capture_handle.setFormatter(EventCore.LOG_FORMATTER)
    log = logging.getLogger('EventCore')
    log.addHandler(capture_handle)
    log.setLevel(log_level)

    log.capture_handle = capture_handle

    return log
