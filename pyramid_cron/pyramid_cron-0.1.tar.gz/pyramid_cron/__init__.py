from __future__ import absolute_import, print_function, division

import logging
import socket
from datetime import datetime

import six

log = logging.getLogger(__name__)


class Task(object):

    def __init__(self, f, min, hour, day, month, dow):
        self.f = f

        class Wildcard(set):

            def __contains__(self, other):
                return True

        wildcard = Wildcard()

        def conv(val):
            if val == '*':
                return wildcard
            if isinstance(val, six.integer_types):
                return set([val])
            if not isinstance(val, set):
                val = set(val)
            return val

        self.min = conv(min)
        self.hour = conv(hour)
        self.day = conv(day)
        self.month = conv(month)
        self.dow = conv(dow)

    def check(self, t):
        return ((t.minute in self.min) and
                (t.hour in self.hour) and
                (t.day in self.day) and
                (t.month in self.month) and
                (t.weekday() in self.dow))

    def go(self, request):
        log.info("%s start", self.f.__name__)
        self.f(dict(request=request, registry=request.registry))
        log.info("%s end", self.f.__name__)


def add_cron_task(config, f, min='*', hour='*', day='*', month='*', dow='*'):
    """
    Register a function for execution by the scheduler.

    Task functions must have the following signature::

        def mytask(system):
            request = system['request']
            registry = system['registry']
            # do stuff

    Additional keys may be added in the future: the single-arg signature
    ensures that task functions will be forward-compatible.

    In addition to the callback function, you can specify a schedule, using a
    cron-like syntax. For the time periods of ``min``, ``hour``, ``day``,
    ``month``, and ``dow`` (day of week), you can specify an integer, a set of
    integers, or the '*' wildcard character. The default argument is '*'. Hours
    are specified in 24-hour time.

    For example, this will run the task every day, at 2:00::

        config.add_cron_task(..., hour=2)

    This will run the task every day at 2:00, 10:00, and 18:00::

        config.add_cron_task(..., hour=[2, 10, 18])

    To run the task 'every 2 hours', you can use ``range()``::

        config.add_cron_task(..., hour=range(0, 24, 2))

    :param f:
        The function to execute. Task functions must have accept a single
        argument, which will be a ``system`` dict containing keys for the
        Pyramid ``request`` and ``registry``.

    :param min:
        Specify which minutes to run the task.

    :param hour:
        Specify which hours to run the task.

    :param day:
        Specify which days to run the task.

    :param month:
        Specify which months to run the task.

    :param dow:
        Specify which days of the week to run the task.
    """
    def register():
        registry = config.registry
        registry.setdefault('cron_tasks', [])
        registry['cron_tasks'].append(Task(f, min=min, hour=hour, day=day,
                                           month=month, dow=dow))
    # This discriminator prevents a task from being registered twice.
    config.action(('cron_task', f), register)


class CronView(object):
    """
    A view to allow the cron signal to be triggered by an HTTP request.
    This is convenient because it means that all the cron stuff happens with
    the webserver's permissions.
    """
    def __init__(self, request):
        self.request = request

    def __call__(self):
        request = self.request
        server_ip = socket.gethostbyname(request.host.split(':')[0])
        allowed = set(['127.0.0.1', '::1', server_ip])
        if request.remote_addr in allowed:
            registry = request.registry
            # This intentionally uses localtime, not UTC.
            t = datetime.now()
            log.warn('begin cron run')
            for task in registry['cron_tasks']:
                if task.check(t):
                    task.go(request)
            log.warn('end cron run')
            return 'ok'
        else:
            return 'fail %s' % request.remote_addr


def includeme(config):
    config.add_route('cron', '/cron')
    config.add_view(CronView, route_name='cron', renderer='string')

    config.add_directive('add_cron_task', add_cron_task)
