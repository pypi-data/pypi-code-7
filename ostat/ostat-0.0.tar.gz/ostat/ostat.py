import math


class OnlineStat(object):
    def __init__(self):
        self.n = 0.0

        self.min = float('inf')
        self.max = float('-inf')

        self.old_m = 0.0
        self.old_s = 0.0

        self.new_m = 0.0
        self.new_s = 0.0

    def push(self, x):
        self.n += 1

        if x < self.min:
            self.min = x
        if x > self.max:
            self.max = x

        self.new_m = self.old_m + (x - self.old_m) / self.n
        self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)

        self.old_m = self.new_m
        self.old_s = self.new_s

    @property
    def mean(self):
        return self.new_m if self.n > 0 else 0.0

    @property
    def variance(self):
        return self.new_s / (self.n) if self.n > 1 else 0.0

    @property
    def stddev(self):
        return math.sqrt(self.variance)

    def __unicode__(self):
        return u'{min} {mean} {max} {stddev}'.format(
            min=self.min,
            mean=self.mean,
            max=self.max,
            stddev=self.stddev,
        )

    def __str__(self):
        return u'{}'.format(self).encode('utf8')

    def __repr__(self):
        return u'<OnlineStat {}>'.format(self)
