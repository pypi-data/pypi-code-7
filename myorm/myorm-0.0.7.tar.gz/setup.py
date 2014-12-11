# coding: utf-8
from setuptools import setup


setupargs = {
    'name': 'myorm',
    'description': 'Provides a simple ORM for MySQL, PostgreSQL and SQLite.',

    'license': 'GPLv3',
    'version': '0.0.7',

    'packages': ['myorm'],

    'author': 'Christian Kokoska',
    'author_email': 'christian@eternalconcert.de',
}

if __name__ == '__main__':
    setup(**setupargs)
