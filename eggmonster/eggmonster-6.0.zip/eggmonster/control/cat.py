"""Dump configuration to stdout."""
import sys

from eggmonster.control._common import get_json, reset_sigpipe

def main():
    reset_sigpipe()
    version, config = get_json('config')
    sys.stdout.write(config)
