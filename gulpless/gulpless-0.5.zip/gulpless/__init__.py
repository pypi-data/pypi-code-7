# coding=utf-8
from __future__ import absolute_import, unicode_literals, division
from gulpless.handlers import Handler, TreeHandler
from gulpless.reactor import Reactor
from gulpless.helpers import gzip


__all__ = ["Handler", "TreeHandler", "Reactor", "gzip"]


def main():
    """Entry point for command line usage."""
    import logging
    import sys
    import os

    sys.path.append(os.getcwd())

    try:
        old, sys.dont_write_bytecode = sys.dont_write_bytecode, True
        import build
    except ImportError:
        sys.exit("No `build.py` found in current folder.")
    finally:
        sys.dont_write_bytecode = old

    try:
        logging.basicConfig(level=build.LOGGING,
                            format="%(message)s")
    except AttributeError:
        logging.basicConfig(level=logging.DEBUG,
                            format="%(message)s")

    reactor = Reactor(build.SRC, build.DEST)
    for handler in build.HANDLERS:
        reactor.add_handler(handler)
    reactor.run("build" in sys.argv)
