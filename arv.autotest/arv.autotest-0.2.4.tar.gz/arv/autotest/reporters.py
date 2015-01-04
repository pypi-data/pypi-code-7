# -*- coding: utf-8 -*-

# $Id$

"""A *reporter* is a class intended to consume the output produced by
a *runner*. Usually a reporter will produce output for human
consumption but it may as well act as a filter for other reporters.

A reporter must define three methods:

:start(): called at the beggining.

:feed(data): process a chunk of data produced by the runner.

:stop(return_code): the runner has finished with ``return_code``.


Ideally:

- the Reporter interface should be redessigned in order to be able to
  chain reporters. Currently reporters must implement that
  funcionality themselves.

- the user should be able to define those chains in the config file

"""

from __future__ import print_function
from datetime import datetime
import os
import sys
import time

from blessings import Terminal


class LineAssemblerReporter(object):
    """Assembles data into lines.

    The purpose of this reporter is assembling chunks of data into
    lines and then feeding them to a wrapped reporter one line at a
    time.

    """

    def __init__(self, wrapped):
        self._wrapped = wrapped
        self._data = []

    def start(self):
        self._wrapped.start()

    def feed(self, data):
        while "\n" in data:
            left, data = data.split("\n", 1)
            self._data.append(left)
            self._data.append("\n")
            self._feed_wrapped()
        if data:
            self._data.append(data)

    def stop(self, code):
        if self._data:
            self._feed_wrapped()
        self._wrapped.stop(code)

    def _feed_wrapped(self):
        self._wrapped.feed("".join(self._data))
        self._data = []


class TerminalReporter(object):
    """Displays data to a terminal.

    This reporter displays the received data into a terminal. On stop
    displays a highlighted message: green indicates success and red
    error.

    """

    def __init__(self, stdout=sys.stdout):
        self.stdout = stdout
        self.term = Terminal(stream=stdout)
        self.counter = 0
        self.width = self.term.width if self.term.is_a_tty else 80 # when testing t.width is None

    def start(self):
        self.counter += 1

    def feed(self, line):
        print(line, file=self.stdout, end="")

    def stop(self, code):
        if code:
            formatter = self.term.bold_white_on_red
            message = "ERROR"
        else:
            formatter = self.term.bold_white_on_green
            message = "OK"
        stamp = "%3i " % self.counter + datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        message = message.center(self.width - 1 - len(stamp), " ")

        print("", file=self.stdout)
        print(formatter(stamp + message), file=self.stdout)


class NullReporter(object):
    """Discards the input it receives.

    This reporter displays a message on start and stop, ignoring the
    input which is feed with. Useful for debuging.

    """
    def __init__(self):
        self.term = Terminal()

    def start(self):
        print(self.term.white_on_blue("Starting null reporter."))

    def feed(self, data):
        pass

    def stop(self, code):
        print(self.term.white_on_blue("Stoping null reporter. Return code: %i" % code))


class DynamicThrottling(object):
    """Dynamically adjust throttling.

    This reporter measures the time required to run the program and
    adjust the throttling rate.

    """
    def __init__(self, throttler, timer=time.time):
        self._start = 0
        self._throttler = throttler
        self._timer = timer

    def start(self):
        self._start = self._timer()

    def feed(self, data):
        pass

    def stop(self, code):
        delta = self._timer() - self._start
        self._throttler.adjust_delta(delta)


class Repeater(object):
    """Chains reporters.
    """
    def __init__(self, *reporters):
        self._reporters = reporters

    def start(self):
        for reporter in self._reporters:
            reporter.start()

    def feed(self, data):
        for reporter in self._reporters:
            reporter.feed(data)

    def stop(self, code):
        for reporter in self._reporters:
            reporter.stop(code)


class DesktopNotifier(object):
    """Notifies test result displaying a message in the desktop.

    Requires the external command 'notify-send'.

    """
    def __init__(self):
        self.notifier = "/usr/bin/notify-send"
        images = os.path.join(os.path.dirname(__file__), "images")
        self.succeed_icon = os.path.join(images, "succeed.png")
        self.failed_icon = os.path.join(images, "failed.png")
        if os.path.isfile(self.notifier):
            self.enabled = True
        else:
            self.enabled = False

    def stop(self, code):
        if self.enabled:
            if code:
                result = "Tests failed!"
                icon = self.failed_icon
            else:
                result = "Tests succeed!"
                icon = self.succeed_icon
            cmd = "killall notify-osd && %s --icon %s '%s'" % (self.notifier, icon, result)
            os.system(cmd)

    def start(self):
        pass

    def feed(self, data):
        pass


class LinePreprocessorReporter(object):
    """Preproccesses lines before displaying them.

    This is a quick hack to be able to remove some lines (action
    'ignore') and highlight others (action 'failure').

    Ideally some kind of plugin architecture should be added in order
    to extend the set of available actions.

    """
    def __init__(self, rules, wrapped):
        self._rules = rules
        self._wrapped = wrapped

    def start(self):
        self._wrapped.start()

    def stop(self, code):
        self._wrapped.stop(code)

    def feed(self, line):
        for rule in self._rules:
            if rule.regex.match(line):
                line = self._process(line, rule.action, rule.params)
                break
        if line is not None:
            self._wrapped.feed(line)

    def _process(self, line, action, args):
        if action == "ignore":
            return None
        if action == "failure":
            return "\033[31m%s\033[0m" % line
        return line
