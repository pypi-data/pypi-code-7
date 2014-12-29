import time


class ExponentialSleep(object):
    def __init__(self, initial=0.1, max=10, multiplier=2.0):
        self.initial = initial
        self.max = max
        self.multiplier = multiplier
        self.num_sleeps = 0
        self.reset()

    def reset(self):
        self.current = self.initial
        self.num_sleeps = 0

    def sleep(self):
        time.sleep(self.current)
        self.current = min(self.current * self.multiplier, self.max)
        self.num_sleeps += 1


class IntervalTracker(object):
    def __init__(self, interval):
        self.interval = interval
        self.last_triggered = time.time()

    def __nonzero__(self):
        return self.is_triggered()

    def is_triggered(self):
        now = time.time()
        return now >= self.last_triggered + self.interval

    def reset(self):
        self.last_triggered = time.time()
