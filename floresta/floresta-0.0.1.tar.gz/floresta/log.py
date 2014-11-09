#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals
import logging


WHITE = '\033[1;37m'
CYAN = '\033[1;36m'
GREEN = '\033[1;32m'
MAGENTA = '\033[1;35m'
YELLOW = '\033[1;33m'
RED = '\033[1;31m'
CLEAR = '\033[0m'


class FlorestaLogHandler(logging.StreamHandler):  # pragma: no cover
    colors = {
        'INFO': GREEN,
        'DEBUG': MAGENTA,
        'WARNING': YELLOW,
        'ERROR': RED,
    }

    def __init__(self, stream, level):
        self.level = level
        super(FlorestaLogHandler, self).__init__(stream)

    def emit(self, record):

        try:
            msg = self.format(record)
            stream = self.stream

            color = self.colors.get(record.levelname, WHITE)
            stream.write("{0}{1}{2}\n".format(color, msg, CLEAR))

            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


logger = logging.getLogger('floresta')
