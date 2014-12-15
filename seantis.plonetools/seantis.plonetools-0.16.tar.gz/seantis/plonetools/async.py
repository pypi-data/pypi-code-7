from logging import getLogger
log = getLogger('seantis.plonetools')

import re
import threading

from ZServer.ClockServer import ClockServer


_clockservers = dict()  # list of registered Zope Clockservers
_lock = threading.Lock()


def clear_clockservers():
    """ Clears the clockservers and connections for testing. """

    with _lock:
        for cs in _clockservers.values():
            cs.close()
        _clockservers.clear()


def register(path, period):
    """ Registers the given path with a clockserver.

    The path must be refer to the local host (think getPhysicalPath).

    Note that due to it's implementation there's no guarantee that the path
    will be called on time every time. The clockserver checks if a call is due
    every time a request comes in, or every 30 seconds when the asyncore.pollss
    path reaches it's timeout (see Lifetime/__init__.py and
    Python Stdlib/asyncore.py).

    The path is going to be called as an Anonymous user, so what can be done
    is very limited, unless seantis.plonetools.unrestricted is use.

    Although this seems to work well it's probably best not to overuse this
    feature. There might be hidden dragons (and crouching tigers).

    """

    if path not in _clockservers:
        with _lock:
            _clockservers[path] = ClockServer(
                path, period, host='localhost', logger=ClockLogger(path)
            )

    return _clockservers[path]


logexpr = re.compile(r'GET [^\s]+ HTTP/[^\s]+ ([0-9]+)')


class ClockLogger(object):

    """ Logs the clock runs by evaluating the log strings. Looks for http
    return codes to do so.

    """

    def __init__(self, path):
        self.path = path

    def return_code(self, msg):
        groups = logexpr.findall(msg)
        return groups and int(groups[0]) or None

    def log(self, msg):
        code = self.return_code(msg)

        if not code:
            log.error("ClockServer for %s returned nothing" % self.path)
        elif code == 200:
            pass
        else:
            log.warn("ClockServer for %s returned %i" % (self.path, code))
