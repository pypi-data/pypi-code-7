from __future__ import unicode_literals

import os
from subprocess import call, check_output

import click

from . import config


@click.command('publish')
@click.option('--branch', nargs=1, default=config['PUBLISH_BRANCH'])
@click.option('--index', nargs=1, default=config['PYPI_INDEX'])
@click.option('--on-tag', is_flag=True)
def publish(branch, index, on_tag):
    if on_tag:
        tag = os.environ.get('TRAVIS_TAG')
        version = check_output('python setup.py --version', shell=True).strip()
        if not tag:
            click.echo('Not on tagged version, not releasing')
            return
        if tag not in ('v{}'.format(version), version):
            click.echo('Tag "{}" != version "v{}"'.format(tag, version))
            return
    elif branch and branch != os.environ.get('TRAVIS_BRANCH', branch):
        click.echo('Not on the publishing branch')
        return
    args = ['python', 'setup.py', 'sdist', 'upload']
    if index:
        args += ['-r', 'alt']
    print ' '.join(args)
    return call(args)
