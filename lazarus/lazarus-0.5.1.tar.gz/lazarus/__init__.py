# coding: utf-8
'''Functions to restart a process when source changes.

Progress doesn't come from early risers - progress is made by lazy men looking
for easier ways to do things.
'''

__version__ = '0.5.1'
import os
import sys
from . import _util
from . import _threading
_as_list = lambda x: list(x) if not isinstance(x, list) else x
_active = False
_close_fds = False
_restart_cb = None
_restart_func = None
_pollthread = None
_mgr = None
_notifier = None


def _reset():
    global _active
    _active = False
    global _close_fds
    _close_fds = False
    global _restart_cb
    _restart_cb = None
    global _restart_func
    _restart_func = None
    global _pollthread
    _pollthread = None
    global _mgr
    _mgr = None
    global _notifier
    _notifier = None


def check_platform():
    '''Checks the platform is Linux.

    For example:

        >>> check_platform()
    '''
    platform = sys.platform
    if not platform.startswith('linux'):
        msg = '%s: unsupported platform'
        raise RuntimeError(msg % platform)


def stop():
    '''Stops lazarus, regardless of which mode it was started in.

    For example:

        >>> import lazarus
        >>> lazarus.default()
        >>> lazarus.stop()
    '''
    global _active
    if not _active:
        msg = 'lazarus is not active'
        raise RuntimeWarning(msg)
    _pollthread.stop()
    _pollthread.join()
    _mgr.close()
    _deactivate()


def _activate():
    global _active
    if _active:
        msg = 'lazarus is already active'
        raise RuntimeWarning(msg)
    _active = True


def _deactivate():
    global _active
    if not _active:
        msg = 'lazarus is not active'
        raise RuntimeWarning(msg)
    _reset()


def _restart():
    if _restart_cb:
        # https://github.com/formwork-io/lazarus/issues/2
        if _restart_cb() is not None:
            return
    _pollthread.stop()
    _mgr.close()
    if _close_fds:
        # close all fds...
        _util.close_fds()

    # declare a mulligan ;)
    if _restart_func:
        _restart_func()
        _deactivate()
    else:
        _util.do_over()


def poll_restart():
    if not _active:
        msg = 'lazarus is not active'
        raise RuntimeWarning(msg)
    if _notifier.check_events(1):
        _notifier.read_events()
        _notifier.process_events()


def default(restart_cb=None, restart_func=None, close_fds=True):
    '''Sets up lazarus in default mode.

    See the :py:func:`custom` function for a more powerful mode of use.

    The default mode of lazarus is to watch all modules rooted at
    ``PYTHONPATH`` for changes and restart when they take place.

    Keyword arguments:

        restart_cb -- Callback invoked prior to restarting the process; allows
        for any cleanup to occur prior to restarting. Returning anything other
        than *None* in the callback will cancel the restart.

        restart_func -- Function invoked to restart the process. This supplants
        the default behavior of using *sys.executable* and *sys.argv*.

        close_fds -- Whether all file descriptors other than *stdin*, *stdout*,
        and *stderr* should be closed

    A simple example:

        >>> import lazarus
        >>> lazarus.default()
        >>> lazarus.stop()
    '''
    check_platform()
    if _active:
        msg = 'lazarus is already active'
        raise RuntimeWarning(msg)

    _python_path = os.getenv('PYTHONPATH')
    if not _python_path:
        msg = 'PYTHONPATH is not set'
        raise RuntimeError(msg)

    if restart_cb and not callable(restart_cb):
        msg = 'restart_cb keyword argument is not callable'
        raise TypeError(msg)

    if restart_func and not callable(restart_func):
        msg = 'restart_func keyword argument is not callable'
        raise TypeError(msg)

    global _close_fds
    _close_fds = close_fds

    try:
        from pyinotify import (
            ProcessEvent,
            WatchManager,
            Notifier,
            IN_MODIFY,
            IN_CLOSE_WRITE,
            IN_CREATE,
            IN_MOVED_TO
        )
    except ImportError as ie:
        msg = 'no pyinotify support (%s)' % str(ie)
        raise RuntimeError(msg)

    class _Handler(ProcessEvent):
        def __init__(self):
            ProcessEvent.__init__(self)

        def process_default(self, event):
            if not _active:
                return
            if event.name.endswith('.py'):
                _restart()

    global _pollthread
    _pollthread = _threading.PollThread(poll_restart)
    global _mgr
    _mgr = WatchManager()
    global _notifier
    _notifier = Notifier(_mgr, _Handler(), timeout=10)
    global _restart_cb
    _restart_cb = restart_cb
    global _restart_func
    _restart_func = restart_func

    evmask = IN_MODIFY | IN_CLOSE_WRITE | IN_CREATE | IN_MOVED_TO
    _mgr.add_watch(_python_path, evmask, rec=True)
    _activate()
    _pollthread.start()


def custom(srcpaths, event_cb=None, poll_interval=1, recurse=True,
           restart_cb=None, restart_func=None, close_fds=True):
    '''Sets up lazarus in custom mode.

    See the :py:func:`default` function for a simpler mode of use.

    The custom mode of lazarus is to watch all modules rooted at any of the
    source paths provided for changes and restart when they take place.

    Keyword arguments:

        event_cb -- Callback invoked when a file rooted at a source path
        changes. Without specifying an event callback, changes to any module
        rooted at a source path will trigger a restart.

        poll_interval -- Rate at which changes will be detected. The default
        value of ``1`` means it may take up to one second to detect changes.
        Decreasing this value may lead to unnecessary overhead.

        recurse -- Whether to watch all subdirectories of every source path for
        changes or only the paths provided.

        restart_cb -- Callback invoked prior to restarting the process; allows
        for any cleanup to occur prior to restarting. Returning anything other
        than *None* in the callback will cancel the restart.

        restart_func -- Function invoked to restart the process. This supplants
        the default behavior of using *sys.executable* and *sys.argv*.

        close_fds -- Whether all file descriptors other than *stdin*, *stdout*,
        and *stderr* should be closed

    An example of using a cleanup function prior to restarting:

        >>> def cleanup():
        ...     pass
        >>> import lazarus
        >>> lazarus.custom(os.curdir, restart_cb=cleanup)
        >>> lazarus.stop()

    An example of avoiding restarts when any ``__main__.py`` changes:

        >>> def skip_main(event):
        ...     if event.name == '__main__.py':
        ...         return False
        ...     return True
        >>> import lazarus
        >>> lazarus.custom(os.curdir, event_cb=skip_main)
        >>> lazarus.stop()
    '''
    check_platform()
    if _active:
        msg = 'lazarus is already active'
        raise RuntimeWarning(msg)

    if restart_cb and not callable(restart_cb):
        msg = 'restart_cb keyword argument is not callable'
        raise TypeError(msg)

    if restart_func and not callable(restart_func):
        msg = 'restart_func keyword argument is not callable'
        raise TypeError(msg)

    global _close_fds
    _close_fds = close_fds

    try:
        from pyinotify import (
            ProcessEvent,
            WatchManager,
            Notifier,
            IN_MODIFY,
            IN_CLOSE_WRITE,
            IN_CREATE,
            IN_MOVED_TO
        )
    except ImportError as ie:
        msg = 'no pyinotify support (%s)' % str(ie)
        raise RuntimeError(msg)

    class _Handler(ProcessEvent):
        def __init__(self):
            ProcessEvent.__init__(self)

        def process_default(self, event):
            if not _active:
                return

            # if caller wants event_cb control, defer _restart logic to them
            if event_cb:
                if event_cb(event):
                    _restart()
                return

            # default logic; _restart on .py events
            if event.name.endswith('.py'):
                _restart()

    global _pollthread
    kwargs = {'poll_interval': poll_interval}
    _pollthread = _threading.PollThread(poll_restart, **kwargs)
    global _mgr
    _mgr = WatchManager()
    global _notifier
    _notifier = Notifier(_mgr, _Handler(), timeout=10)
    global _restart_cb
    _restart_cb = restart_cb

    evmask = IN_MODIFY | IN_CLOSE_WRITE | IN_CREATE | IN_MOVED_TO
    srcpaths = _as_list(srcpaths)
    kwargs = {}
    if recurse:
        kwargs['rec'] = True
    for srcpath in srcpaths:
        _mgr.add_watch(srcpath, evmask, **kwargs)
    _activate()
    _pollthread.start()
