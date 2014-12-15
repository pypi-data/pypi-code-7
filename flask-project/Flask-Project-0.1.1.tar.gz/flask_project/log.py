# coding=utf-8
from __future__ import unicode_literals
import logging


LONG_LOG_FORMAT = '%(asctime)s - [%(name)s.%(levelname)s] [%(threadName)s, %(module)s.%(funcName)s@%(lineno)d] %(message)s'


def get_logger(name='main', level=logging.DEBUG, fmt='%(message)s'):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if len(logger.handlers) > 0:
        return logger

    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter(fmt)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger