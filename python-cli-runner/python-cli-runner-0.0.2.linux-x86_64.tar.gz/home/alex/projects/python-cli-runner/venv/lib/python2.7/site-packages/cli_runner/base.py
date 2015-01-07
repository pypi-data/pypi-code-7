# encoding: utf-8

from __future__ import unicode_literals
from sys import modules
from os.path import basename, splitext
from weakref import WeakValueDictionary

from six import with_metaclass
from docopt import docopt

from cli_runner.tools import unwrap_text


class ServiceRegister(type):
    services = WeakValueDictionary()

    def __new__(mcls, name, bases, namespace):
        abstract = namespace.pop('abstract', False)
        Class = super(ServiceRegister, mcls).__new__(mcls, name, bases, namespace)
        if not abstract:
            name = Class.get_name()
            if name in mcls.services:
                raise TypeError('Service name "{}" already exists!'.format(name))
            mcls.services[name] = Class
        return Class

    def __iter__(self):
        return iter(self.services)


class BaseService(with_metaclass(ServiceRegister, object)):
    abstract = True
    help = None
    name = None

    def __init__(self):
        self.arguments = self.get_arguments()

    def run(self):
        raise NotImplementedError

    def stop(self):
        pass

    def get_arguments(self):
        return {}

    @classmethod
    def get_name(cls):
        if cls.name is not None:
            return cls.name
        return splitext(basename(modules[cls.__module__].__file__))[0]

    @classmethod
    def short_description(cls):
        description = cls.help or ''
        description = description.strip().splitlines()
        return description[0] if description else ''


class NoArgumentService(BaseService):
    abstract = True


class DocoptService(BaseService):
    abstract = True

    def get_arguments(self):
        from sys import argv
        return docopt(unwrap_text(self.help), argv[2:])
