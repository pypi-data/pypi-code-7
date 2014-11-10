# -*- coding: utf-8 -*-

import click
import subprocess

COMMANDS = {
    'show_connections': "netstat -anlp | tr -s ' ' | cut -d ' ' -f 5 | grep ':' | cut -d ':' -f 1 | sort | uniq -c | sort -n",
    }


@click.group()
def root():
    pass


def build_command(name, command):
    def _():
        return subprocess.Popen(command, shell=True)
    _.__name__ = name
    _ = click.command()(_)
    root.add_command(_)

for name, command in COMMANDS.iteritems():
    build_command(name, command)

if __name__ == '__main__':
    root()
