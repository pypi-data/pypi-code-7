# -*- coding: utf-8 -*-

import redis
import click
import subprocess

from .utils import cut_list

COMMANDS = {
    'show_connections': "netstat -anlp | tr -s ' ' | cut -d ' ' -f 5 | grep ':' | cut -d ':' -f 1 | sort | uniq -c | sort -n",
    }


@click.group()
def root():
    pass


@click.command()
def migrate_redis(from_redis, to_redis):
    from_client = redis.Redis.from_url(from_redis)
    to_client = redis.Redis.to_redis(to_redis)

    keys = from_client.keys()

    for smaller_keys in cut_list(keys, 1000):
        values = from_client.mget(keys)
        to_client.mset(dict(zip(smaller_keys, values)))

root.add_command(migrate_redis)


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
