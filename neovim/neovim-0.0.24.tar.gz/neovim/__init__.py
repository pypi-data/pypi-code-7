"""Python client for Nvim.

Client library for talking with Nvim processes via it's msgpack-rpc API.
"""
import logging
import os
import sys

from .api import DecodeHook, Nvim, SessionHook
from .msgpack_rpc import (socket_session, spawn_session, stdio_session,
                          tcp_session)
from .plugin import (Host, autocmd, command, encoding, function, plugin,
                     rpc_export, shutdown_hook)


__all__ = ('tcp_session', 'socket_session', 'stdio_session', 'spawn_session',
           'start_host', 'autocmd', 'command', 'encoding', 'function',
           'plugin', 'rpc_export', 'Host', 'DecodeHook', 'Nvim',
           'SessionHook', 'shutdown_hook')


def start_host(session=None):
    """Promote the current process into python plugin host for Nvim.

    Start msgpack-rpc event loop for `session`, listening for Nvim requests
    and notifications. It registers Nvim commands for loading/unloading
    python plugins.

    The sys.stdout and sys.stderr streams are redirected to Nvim through
    `session`. That means print statements probably won't work as expected
    while this function doesn't return.

    This function is normally called at program startup and could have been
    defined as a separate executable. It is exposed as a library function for
    testing purposes only.
    """
    plugins = []
    for arg in sys.argv:
        _, ext = os.path.splitext(arg)
        if ext == '.py':
            plugins.append(arg)

    if not plugins:
        sys.exit('must specify at least one plugin as argument')

    logger = logging.getLogger(__name__)
    if 'NVIM_PYTHON_LOG_FILE' in os.environ:
        logfile = os.environ['NVIM_PYTHON_LOG_FILE'].strip()
        handler = logging.FileHandler(logfile, 'w')
        handler.formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s @ '
            '%(filename)s:%(funcName)s:%(lineno)s] %(process)s - %(message)s')
        logging.root.addHandler(handler)
        level = logging.INFO
        if 'NVIM_PYTHON_LOG_LEVEL' in os.environ:
            l = getattr(logging,
                        os.environ['NVIM_PYTHON_LOG_LEVEL'].strip(),
                        level)
            if isinstance(l, int):
                level = l
        logger.setLevel(level)
    if not session:
        session = stdio_session()
    host = Host(Nvim.from_session(session))
    host.start(plugins)


# Required for python 2.6
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


if not logging.root.handlers:
    logging.root.addHandler(NullHandler())
