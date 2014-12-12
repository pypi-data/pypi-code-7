# coding: utf-8
from __future__ import print_function
import threading
import time
from Queue import Queue


class Executor(object):
    def start(self):
        pass


class TaskPool(object):
    """TODO: concurrent queue"""

    def __init__(self):
        self._queue = Queue()

    def push(self, task):
        self._queue.put(task)

    def poll(self):
        if self._queue.qsize() > 0:
            try:
                return self._queue.get_nowait()
            except Exception as e:
                return None
        else:
            return None

    def is_empty(self):
        return self._queue.qsize() < 1

    def available(self):
        return self._queue.qsize() > 0


class TaskThread(threading.Thread):
    def __init__(self, task_pool):
        threading.Thread.__init__(self)
        self._task_pool = task_pool

    def run(self):
        while True:
            task = self._task_pool.poll()
            if task is not None:
                task()
            time.sleep(0.05)


class FixedThreadsExecutor(Executor):
    """TODO: check thread status and create new thread if some died"""

    def __init__(self, thread_count):
        self._thread_count = thread_count if thread_count > 0 else 1
        self._threads = []
        self._task_pool = TaskPool()

    def _init_threads(self):
        for i in range(self._thread_count):
            t = TaskThread(self._task_pool)
            self._threads.append(t)
            t.start()

    def start(self):
        self._init_threads()

    def submit(self, task):
        self._task_pool.push(task)