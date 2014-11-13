# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for the Juju Quickstart jenv generated files handling."""

from __future__ import unicode_literals

import unittest

import yaml

from quickstart.models import jenv
from quickstart.tests import helpers


class TestExists(helpers.JenvFileTestsMixin, unittest.TestCase):

    def test_found(self):
        # True is returned if the jenv file exists.
        with self.make_jenv('ec2', ''):
            exists = jenv.exists('ec2')
        self.assertTrue(exists)

    def test_not_found(self):
        # False is returned if the jenv file does not exist.
        with self.make_jenv('ec2', ''):
            exists = jenv.exists('local')
        self.assertFalse(exists)


class TestGetValue(
        helpers.JenvFileTestsMixin, helpers.ValueErrorTestsMixin,
        unittest.TestCase):

    def test_whole_content(self):
        # The function correctly returns the whole jenv content.
        with self.make_jenv('local', yaml.safe_dump(self.jenv_data)):
            data = jenv.get_value('local')
        self.assertEqual(self.jenv_data, data)

    def test_section(self):
        # The function correctly returns a whole section.
        with self.make_jenv('ec2', yaml.safe_dump(self.jenv_data)):
            data = jenv.get_value('ec2', 'bootstrap-config')
        self.assertEqual(self.jenv_data['bootstrap-config'], data)

    def test_value(self):
        # The function correctly returns a value in the root node.
        with self.make_jenv('ec2', yaml.safe_dump(self.jenv_data)):
            value = jenv.get_value('ec2', 'user')
        self.assertEqual('admin', value)

    def test_section_value(self):
        # The function correctly returns a section value.
        with self.make_jenv('ec2', yaml.safe_dump(self.jenv_data)):
            value = jenv.get_value('ec2', 'bootstrap-config', 'admin-secret')
        self.assertEqual('Secret!', value)

    def test_nested_section(self):
        # The function correctly returns nested section's values.
        with self.make_jenv('hp', yaml.safe_dump(self.jenv_data)):
            value = jenv.get_value('hp', 'life', 'universe', 'everything')
        self.assertEqual(42, value)

    def test_file_not_found(self):
        # A ValueError is raised if the jenv file cannot be found.
        expected_error = 'unable to open file'
        with self.make_jenv('hp', yaml.safe_dump(self.jenv_data)):
            with self.assertRaises(ValueError) as context_manager:
                jenv.get_value('local')
        self.assertIn(expected_error, bytes(context_manager.exception))

    def test_section_not_found(self):
        # A ValueError is raised if the specified section cannot be found.
        with self.make_jenv('local', yaml.safe_dump(self.jenv_data)) as path:
            expected_error = (
                'invalid YAML contents in {}: no-such key not found in the '
                'root section'.format(path))
            with self.assert_value_error(expected_error):
                jenv.get_value('local', 'no-such')

    def test_subsection_not_found(self):
        # A ValueError is raised if the specified subsection cannot be found.
        with self.make_jenv('local', yaml.safe_dump(self.jenv_data)) as path:
            expected_error = (
                'invalid YAML contents in {}: series key not found in the '
                'bootstrap-config section'.format(path))
            with self.assert_value_error(expected_error):
                jenv.get_value('local', 'bootstrap-config', 'series')

    def test_invalid_yaml_contents(self):
        # A ValueError is raised if the jenv file is not well formed.
        expected_error = 'unable to parse file'
        with self.make_jenv('ec2', ':'):
            with self.assertRaises(ValueError) as context_manager:
                jenv.get_value('ec2')
        self.assertIn(expected_error, bytes(context_manager.exception))
