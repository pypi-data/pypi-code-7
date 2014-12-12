# coding: utf-8
from __future__ import print_function
import logging
from Queue import Queue
import threading
import time
import functools
from . import threadpool
from datetime import datetime, timedelta

thread_pool = threadpool.FixedThreadsExecutor(4)
thread_pool.start()


def print_result(req, result):
    print("the result of %s is %s" % (str(req), str(result)))


class AbstractPool(object):
    def __init__(self):
        self._messages = Queue()
        self._listeners = {}

    def add_listener(self, interest, listener):
        self._listeners[interest] = listener

    def offer_message(self, msg):
        if msg is None:
            return
        listener = self._listeners.get(self.message_key_type(msg))
        if listener is not None:
            thread_pool.submit(listener.create_process_message_task(msg))
        other_listener = self._listeners.get(object)
        if other_listener is not None:
            thread_pool.submit(other_listener.create_process_message_task(msg))

    def offer_messages(self, msgs):
        for msg in msgs:
            self.offer_message(msg)

    def take_message(self):
        if self.available():
            return self._messages.get_nowait()
        else:
            return None

    def is_empty(self):
        return self._messages.qsize() < 1

    def available(self):
        return not self.is_empty()

    def message_key_type(self, msg):
        pass


class ChannelMessagePool(AbstractPool):
    def message_key_type(self, msg):
        return type(msg[1])


class ReceiveMessagePool(ChannelMessagePool):
    pass


class SendMessagePool(ChannelMessagePool):
    pass


class AutoClosePool(object):
    """TODO: concurrent"""

    def __init__(self, timeout_milliseconds=5000, close_fn=None):
        from .threadpool import FixedThreadsExecutor

        self.timeout_milliseconds = timeout_milliseconds
        self.close_fn = close_fn
        self.stopped = False
        self.close_lock = threading.Lock()
        self.pool_objects = {}
        self.executor = FixedThreadsExecutor(4)

        def check_close_task(pool):
            while pool.is_running():
                try:
                    pool.check_closed()
                except Exception as e:
                    pass
                time.sleep(1)

        self.executor.submit(functools.partial(check_close_task, self))
        self.executor.start()

    def is_running(self):
        return not self.stopped

    def stop(self):
        self.stopped = True

    def put(self, key, value):
        if key is not None:
            self.pool_objects[key] = (value, datetime.now())

    def remove(self, key):
        if key is None:
            return None
        pair = self.pool_objects.get(key)
        if pair is None:
            return None
        del self.pool_objects[key]
        return pair[0]

    def _is_available_pair(self, pair):
        if pair is None:
            return False
        update_time = pair[1]
        if update_time is None:
            return False
        expired_time = update_time + timedelta(milliseconds=self.timeout_milliseconds)
        if expired_time > datetime.now():
            return pair[0] is not None
        else:
            return False

    def get(self, key):
        pair = self.pool_objects.get(key, None)
        if pair is None:
            return None
        return pair[0] if self._is_available_pair(pair) else None

    def check_closed(self):
        for (key, pair) in self.pool_objects:
            if key is None:
                continue
            if not self._is_available_pair(pair):
                self.close_lock.acquire()
                try:
                    val = pair[0]
                    if self.close_fn is not None:
                        try:
                            self.close_fn(val)
                        except Exception as e:
                            pass
                    del self.pool_objects[key]
                finally:
                    self.close_lock.release()


class RpcTaskPool(AutoClosePool):
    pass