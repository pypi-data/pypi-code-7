import time
from .stream import send_time

class Profiler(object):
    def __init__(self, metric):
        self.metric = metric
        self.start_stamp = None

    def __enter__(self):
        self.start_stamp = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_stamp) * 1000  # msec

        send_time(self.metric,
                  duration)
