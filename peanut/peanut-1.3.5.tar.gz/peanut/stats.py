# -*- coding: utf-8 -*-


__author__ = "Johannes Köster"
__license__ = "MIT"


import time
from collections import defaultdict


class Stats:

    def __init__(self):
        self.records = defaultdict(list)
        self.cl = None
        self.start = "{}_start".format
        self.duration = "{}_duration".format

    def start_timer(self, name):
        self.barrier()
        self.records[self.start(name)].append(time.time())

    def stop_timer(self, name):
        self.barrier()
        t0 = self.records[self.start(name)][-1]
        t1 = time.time()
        self.records[self.duration(name)].append(t1 - t0)

    def record_value(self, name, value):
        self.records[name].append(value)

    def write(self, path):
        with open(path, "w") as f:
            for name, values in self.records.items():
                print(name, *values, sep="\t", file=f)

    def barrier(self):
        if self.cl is not None:
            self.cl.barrier()

stats = Stats()
