import random

import click


def generate_password(length=4):
    with open('/usr/share/dict/words') as fp:
        words = fp.readlines()

    return " ".join([random.choice(words).strip() for x in range(length)])


@click.command()
@click.argument('length', default=4, type=click.IntRange(1,10))
def main(length):
    """Generate passwords such as correct horse battery staple"""
    click.echo(generate_password(length))
