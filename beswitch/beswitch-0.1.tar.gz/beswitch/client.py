import importlib
import os.path
import sys


class Client:

    stack = []

    def __init__(self, client_name):
        self.name = client_name
        self.module = sys.modules[self.name]
        self.root = os.path.dirname(os.path.abspath(self.module.__file__))
        self.frontend = "frontend"
        self.backends = "backends"
        self.chain = []

    def derive(self, full_backend_name, parent_backend_name=None):
        backend = sys.modules[full_backend_name]
        if parent_backend_name is None:
            self.load_frontend(recipient=backend)
        else:
            self.load_backend(parent_backend_name, recipient=backend)

    def flush_chain(self):
        frontend_path = os.path.join(self.root, self.frontend)
        self.chain[0].__path__.append(frontend_path)
        for parent, child in zip(self.chain, self.chain[1:]):
            child.__path__ += parent.__path__

    def load_backend(self, backend_name, recipient):
        self.load_module(self.backends + "." + backend_name, recipient)

    def load_frontend(self, recipient):
        self.load_module(self.frontend, recipient)

    def load_module(self, module_name, recipient):

        def clone_attributes(source, target):
            if not hasattr(source, "__all__"):
                return
            target.__all__ = source.__all__
            for attribute in source.__all__:
                setattr(target, attribute, getattr(source, attribute))

        self.chain.insert(0, recipient)
        if module_name == self.frontend:
            self.flush_chain()

        full_module_name = ".".join([self.name, module_name])
        module = importlib.import_module(full_module_name)
        clone_attributes(module, recipient)

    def select(self, backend_name):
        self.load_backend(backend_name, recipient=self.module)
