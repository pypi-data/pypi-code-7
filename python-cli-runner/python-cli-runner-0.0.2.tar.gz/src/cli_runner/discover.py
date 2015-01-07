# encoding: utf-8


class BaseDiscover(object):
    def __init__(self, **kwargs):
        pass

    def discover(self):
        for module in self.find_modules():
            if not self.is_should_import(module):
                continue
            self.process_module(self.import_module(module))

    def is_should_import(self, module):
        return module

    def find_modules(self):
        yield

    def import_module(self, module):
        pass

    def process_module(self, module):
        pass


class AutoDiscover(BaseDiscover):
    def __init__(self, packages, **kwargs):
        super(AutoDiscover, self).__init__(**kwargs)
        self.packages = packages or ()

    def find_modules(self):
        from pkgutil import walk_packages

        for package in self.packages:
            prefix = '{}.'.format(package)
            package = __import__(package)

            for _, name, is_pkg in walk_packages(package.__path__, prefix):
                if is_pkg:
                    continue
                yield name

        yield

    def import_module(self, module):
        __import__(module)
