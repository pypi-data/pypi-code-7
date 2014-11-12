import inspect

import beswitch.client


def select(backend_name):
    Client = beswitch.client.Client
    client_name = inspect.getmodule(inspect.stack()[1][0]).__name__
    Client.stack.append(Client(client_name))
    Client.stack[-1].select(backend_name)
    Client.stack.pop()


def derive(parent_backend_name=None):
    Client = beswitch.client.Client
    full_backend_name = inspect.getmodule(inspect.stack()[1][0]).__name__
    Client.stack[-1].derive(full_backend_name, parent_backend_name)
