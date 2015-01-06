from __future__ import unicode_literals

import click
import os

from . import config


@click.command('create-pypi')
@click.option('--username', nargs=1, default=config['PYPI_USERNAME'])
@click.option('--password', nargs=1, default=config['PYPI_PASSWORD'])
@click.option('--index', nargs=1, default=config['PYPI_INDEX'])
@click.option('--server', nargs=1, default=config['PYPI_SERVER'])
@click.option('--base-dir', nargs=1, default='~/')
@click.option('--dry', nargs=1, type=bool, default=False)
def create_pypi(username, password, index, server, base_dir, dry):
    root = os.path.expanduser(base_dir + '.pip')

    os.path.exists(root) or (dry or os.mkdir(root))

    files = [
        (
            os.path.join(os.path.expanduser(base_dir), '.pypirc'),
            [
                '[distutils]',
                'index-servers=',
                '\talt' if index else '\tpypi',
                '',
                '[alt]' if index else '[pypi]',
                'repository: {}'.format(server) if server else '',
                'username: {}'.format(username),
                'password: {}'.format(password)
            ]
        )
    ]
    if index:
        files += [
            (
                os.path.join(os.path.expanduser(base_dir), '.pydistutils.cfg'),
                [
                    '[easy_install]',
                    'index_url = https://{}:{}@{}'.format(
                        username, password, index
                    )
                ]
            ),
            (
                os.path.join(root, 'pip.conf'),
                [
                    '[global]',
                    'extra-index-url = https://{}:{}@{}'.format(
                        username, password, index
                    )
                ]
            )
        ]

    for file_path, contents in files:
        with open(file_path, 'w') as f:
            if dry:
                print ''
                print file_path
            for line in contents:
                if dry:
                    print line
                else:
                    f.write(line)
                    f.write('\n')
            if not dry:
                click.echo('wrote {}'.format(file_path))

    click.echo('created pypi setup files')
