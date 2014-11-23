# -*- coding: utf-8 -*-
import os
import sys
import json

from .logger import log


class ConfigLoader(object):
    def __init__(self, path='~/.crunner.json'):
        self.path = path.replace('~', os.path.expanduser('~'))

    def load(self):
        if not os.path.exists(self.path):
            log.error("File ~/.crunner.json doesn't exist")
            sys.exit(1)
        config_data = self._read_config_file()
        main, notifier, tester, projects = self._parse_config_data(config_data)
        self._validate_config_data(main, notifier, tester, projects)
        return main, notifier, tester, projects

    def _read_config_file(self):
        try:
            with open(self.path, 'r') as f:
                return json.loads(f.read())
        except ValueError as e:
            log.error("Cannot read configuration.\nReturned error is:\n    {}".format(e.message))
            sys.exit(2)

    def _parse_config_data(self, config_data):
        return config_data.get('main'), config_data.get('notifier'), config_data.get('tester'), config_data.get('projects', {})

    def _validate_config_data(self, main, notifier, tester, projects):
        if notifier is None or tester is None:
            log.error("Wrong configuration syntax: no notifier/tester sections.")
            sys.exit(3)
        validation_result = self._check_main(main)
        validation_result += self._check_notifier(notifier)
        validation_result += self._check_tester(tester)
        validation_result += self._check_projects(projects)
        if validation_result:
            self._handle_config_error(validation_result)
        return notifier, tester, projects

    def _check_notifier(self, notifier):
        keys = ['cmd', 'img_arg', 'msg_arg', 'add_args']
        return self._are_keys_exist('notifier', notifier, keys)

    def _check_tester(self, tester):
        keys = ['cmd', 'args']
        return self._are_keys_exist('tester', tester, keys)

    def _check_projects(self, projects):
        keys = ['active', 'test_path', 'project_path', 'watching_types']
        result = []
        for name, settings in projects.items():
            project_result = self._are_keys_exist(name, settings, keys)
            if project_result:
                result += project_result
        return result

    def _are_keys_exist(self, name, data, keys):
        result = []
        for key in keys:
            if key not in data:
                result.append("      Key ({}) is required for ({}) but doesn't exist.".format(key, name))
        return result

    def _handle_config_error(self, result):
        log.error('\nFound error in configuration:\n' +
                  '\n'.join(result) +
                  '\n')
        sys.exit(4)

    def _check_main(self, main):
        keys = ['run_on_start', 'delay']
        return self._are_keys_exist('main', main, keys)
