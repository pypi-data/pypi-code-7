""" Support configuration files in Bottle. """

# Package information
# ===================

__version__ = "0.1.2"
__project__ = "bottle-config"
__author__ = "Kirill Klenov <horneds@gmail.com>"
__license__ = "MIT"


from importlib import import_module
import os


class Config(object):

    """ Initialize an application's configuration. """

    name = 'config'
    api = 2

    def __init__(self, module='settings'):
        """ Init settings module. """
        self.module = module

    def setup(self, app):
        """ Load a configuration. """
        module = import_module(os.environ.get('BOTTLE_CONFIG', self.module))
        for name in dir(module):
            if name == name.upper():
                app.config.update({name: getattr(module, name)})

    @staticmethod
    def apply(callback, route):
        """ Just do nothing. """
        return callback

# Default configuration instance
config = Config()
