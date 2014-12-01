import logging
import logging.handlers


class WaitingConfigurationHandler(logging.handlers.MemoryHandler):
    '''This class keeps logs in memory until we have a configuration.'''

    def __init__(self):
        '''We initialize a memory handler with no targets.'''
        logging.handlers.MemoryHandler.__init__(self, 3)
        self.targets = []

    def setTargets(self, targets):
        '''We can reset targets whenever we want.'''
        self.targets = targets

    def flushAll(self):
        '''For all targets, we send the buffer.'''
        for target in self.targets:
            for record in self.buffer:
                target.emit(record)
        self.buffer = []

    def flush(self):
        pass
