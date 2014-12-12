# coding: utf-8
from __future__ import print_function
import json
import time
from datetime import datetime, timedelta


def try_parse_json(text):
    if text is None:
        return None
    try:
        return json.loads(text)
    except Exception as e:
        return None


def safeunicode(obj, encoding='utf-8'):
    r"""
    Converts any given object to unicode string.

        >>> safeunicode('hello')
        u'hello'
        >>> safeunicode(2)
        u'2'
        >>> safeunicode('\xe1\x88\xb4')
        u'\u1234'
    """
    t = type(obj)
    if t is unicode:
        return obj
    elif t is str:
        return obj.decode(encoding, 'ignore')
    elif t in [int, float, bool]:
        return unicode(obj)
    elif hasattr(obj, '__unicode__') or isinstance(obj, unicode):
        try:
            return unicode(obj)
        except Exception as e:
            return u""
    else:
        return str(obj).decode(encoding, 'ignore')


class TimeoutException(Exception):
    pass


class ValueFuture(object):
    def __init__(self):
        self.fulfill_callbacks = []
        self.reject_callbacks = []
        self.value = None
        self._is_done = False

    def done(self):
        self._is_done = True

    def is_done(self):
        return self._is_done

    def set(self, value):
        self.value = value

    def set_result(self, value):
        if self.is_done():
            return
        self.set(value)
        self.done()
        self.call_fulfills(value)

    def call_fulfills(self, value):
        for fulfill in self.fulfill_callbacks:
            if fulfill is not None:
                try:
                    fulfill(value)
                except Exception as e:
                    pass

    def call_rejects(self, exception):
        for reject in self.reject_callbacks:
            if reject is not None:
                try:
                    reject(exception)
                except Exception as e:
                    pass

    def cancel(self, may_interrupt_if_running=False):
        self._is_done = True
        self.call_rejects(Exception('future task canceled'))

    def get(self, timeout=5000):
        if self.is_done():
            return self.value
        start_time = datetime.now()

        def timedout():
            return start_time + timedelta(milliseconds=timeout) < datetime.now()

        while not self.is_done() and not timedout():
            time.sleep(0.05)
        if not self.is_done():
            raise TimeoutException()
        return self.value

    def fulfill(self, callback):
        if callback is not None:
            self.fulfill_callbacks.append(callback)
            if self.is_done():
                try:
                    callback(self.get())
                except Exception as e:
                    pass

    def reject(self, callback):
        if callback is not None:
            self.reject_callbacks.append(callback)