# -*- coding: utf-8 -*-
from watchdog.observers import Observer


class FileWatcher(object):
    def __init__(self, path, event):
        self.event = event
        self.path = path
        self.observer = None

    def start(self):
        if self.observer is None:
            self.observer = Observer()
            self.observer.schedule(self.event, self.path, recursive=True)
            self.observer.start()

    def stop(self):
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
