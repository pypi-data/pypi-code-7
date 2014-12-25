#!/usr/bin/env python

# Copyright (C) 2014 Miguel Angel Garcia <miguelangel.garcia@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import argparse
import jinja2
import logging

import inquirer

from version import APP

LOGGER = logging.getLogger(__name__)


class Loader(object):
    def __init__(self, path):
        self._path = path

    @property
    def config(self):
        filename = os.path.join(self._path, 'settings.py')
        config = {}
        a = {}
        with open(filename) as fd:
            exec(fd.read(), {}, config)
        return config

    @property
    def file_path(self):
        return os.path.join(self._path, 'files')


class Runner(object):
    def __init__(self, loader):
        self._loader = loader
        self._config = None
        self._variables = None

    def run(self, output):
        self.load_config()
        self.inquire()
        self.generate(output)

    def load_config(self):
        self._config = self._loader.config

    def inquire(self):
        questions = self._config.get('QUESTIONS')
        if questions is None:
            return
        if isinstance(questions, str):
            q = inquirer.load_from_json(questions)
            self._variables = inquirer.prompt(q)
        if isinstance(questions, list):
            q = inquirer.questions.load_from_list(questions)
            self._variables = inquirer.prompt(q)

    def generate(self, output):
        basepathlen = len(self._loader.file_path) + 1
        for root, dirs, files in os.walk(self._loader.file_path):
            for d in dirs:
                origin = os.path.join(root, d)
                path = os.path.join(output, origin[basepathlen:])
                if not os.path.exists(path):
                    LOGGER.info('Creating directory %s', path)
                    os.makedirs(path)
            for f in files:
                origin = os.path.join(root, f)
                path = os.path.join(output, origin[basepathlen:])
                with open(origin) as fd:
                    if path.endswith('.jinja'):
                        target = path[:-len('.jinja')]
                        LOGGER.info('Applying template %s to %s',
                                    origin, target)
                        template = jinja2.Template(fd.read())
                        content = template.render(self._variables)
                    else:
                        target = path
                        LOGGER.info('Copying file %s to %s', origin, target)
                        content = fd.read()
                if os.path.exists(target):
                    LOGGER.info(
                        'File "%s" already exists and will not be overriden.',
                        target)
                    continue
                with open(target, 'w+') as fd:
                    fd.write(content)


def logging_setup(verbose):
    if verbose:
        FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
        DATEFORMAT = ''
        LEVEL = logging.DEBUG
    else:
        FORMAT = '%()s %(message)s'
        DATEFORMAT = ''
        LEVEL = logging.INFO
    formatter = logging.Formatter(FORMAT, DATEFORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)
    LOGGER.setLevel(LEVEL)
    LOGGER.debug('Verbose mode activated')


def main():
    parser = argparse.ArgumentParser(description=APP.description)
    parser.add_argument('--template-path', dest="path", required=True,
                        help='Path to template to be applied.')

    parser.add_argument('-o', '--output',
                        help='Where the output should be put.')

    parser.add_argument('--verbose', action="store_true", default=False,
                        help='Verbose mode.')

    args = parser.parse_args()

    logging_setup(args.verbose)

    loader = Loader(args.path)
    runner = Runner(loader)
    runner.run(args.output)


if __name__ == '__main__':
    main()
