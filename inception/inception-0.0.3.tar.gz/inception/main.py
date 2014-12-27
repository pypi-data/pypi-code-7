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
import subprocess
import inquirer

from version import APP

LOGGER = logging.getLogger(__name__)


class Variables(dict):
    _instance = None

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super(Variables, cls).__new__(cls, **kwargs)
        return cls._instance

    def reset(self):
        self.clear()


class CallRun(object):
    def __init__(self, command):
        self._command = command

    def __call__(self, config, template_path, output):
        LOGGER.debug('running CallRun("%s")', self._command)
        return subprocess.check_call(self._command, shell=True, cwd=output)


class CallCopy(object):
    def __init__(self, source='files'):
        self._source = source

    def __call__(self, config, template_path, output):
        source = os.path.join(template_path, self._source)
        LOGGER.debug('running CallCopy("%s")', source)
        basepathlen = len(source) + 1
        for root, dirs, files in os.walk(source):
            for d in dirs:
                origin = os.path.join(root, d)
                path = os.path.join(output, self._parse(origin[basepathlen:]))
                if not os.path.exists(path):
                    LOGGER.info('Creating directory %s', path)
                    os.makedirs(path)
            for f in files:
                origin = os.path.join(root, f)
                path = os.path.join(output, self._parse(origin[basepathlen:]))
                with open(origin) as fd:
                    if path.endswith('.jinja'):
                        target = path[:-len('.jinja')]
                        LOGGER.info('Applying template %s to %s',
                                    origin, target)
                        content = self._parse(fd.read())
                    else:
                        target = path
                        LOGGER.info('Copying file %s to %s', origin, target)
                        content = fd.read()
                if os.path.exists(target):
                    LOGGER.warning(
                        'File "%s" already exists and will not be overriden.',
                        target)
                    continue
                self._write_result(target, content, origin)

    def _parse(self, template):
        return jinja2.Template(template).render(Variables())

    def _write_result(self, target, content, origin):
        with open(target, 'w+') as fd:
            fd.write(content)
        os.chmod(target,  os.stat(origin).st_mode)


class CallPrompt(object):
    def __init__(self, questions=None):
        self._questions = questions

    def __call__(self, config, template_path, output):
        questions = self._questions or config.get('QUESTIONS')
        if questions is None:
            LOGGER.debug('No questions to prompt')
            return

        if isinstance(questions, str):
            q = inquirer.load_from_json(questions)
        if isinstance(questions, list):
            q = inquirer.questions.load_from_list(questions)
        Variables().update(inquirer.prompt(q))


COMMANDS = dict(
    run=CallRun,
    copy=CallCopy,
    prompt=CallPrompt,
)


class Loader(object):
    def __init__(self, path):
        self.path = path

    @property
    def config(self):
        filename = os.path.join(self.path, 'settings.py')
        config = {}
        with open(filename) as fd:
            exec(fd.read(), COMMANDS.copy(), config)
        return config


class Runner(object):
    def __init__(self, loader):
        self._loader = loader
        self._config = loader.config

    def run(self, output):
        program = self._config.get('PROGRAM') or [CallPrompt(), CallCopy()]

        for command in program:
            LOGGER.debug('New program command: %s', command)
            if callable(command):
                command(self._config, self._loader.path, output)
                continue
            else:
                LOGGER.error('Unsupported command: %s', command)


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
