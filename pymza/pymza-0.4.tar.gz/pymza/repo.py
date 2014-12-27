import os
from ConfigParser import SafeConfigParser


from .task import TaskCode


class Repo(object):
    def __init__(self, home=None, debug=False):
        self.home = os.path.abspath(home or '.')
        self.debug = debug
        self.config = SafeConfigParser()
        self.config.readfp(open(os.path.join(self.home, 'repo.ini')))

    def load_task(self, name):
        return TaskCode(__import__(name, globals(), {}, [], -1))

    def tasks(self):
        return [self.config.get(x, 'task').strip() for x in self.config.sections()]

    def state_dir(self):
        path = self.config.get('DEFAULT', 'state_dir') or './state'
        return os.path.join(self.home, path)
