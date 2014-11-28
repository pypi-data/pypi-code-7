# -*- coding: utf-8 -*-

from collections import defaultdict

import logging


class LogCountHandler(logging.Handler):
    def __init__(self):
        super(LogCountHandler, self).__init__()
        self._counter = defaultdict(int)

    def emit(self, record):
        for lvl in record.levelno, record.levelname:
            self._counter[lvl] += 1

    def count(self, lvl):
        return self._counter.get(lvl, 0)
