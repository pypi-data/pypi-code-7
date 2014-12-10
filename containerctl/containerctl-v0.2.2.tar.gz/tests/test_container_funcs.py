"""Test container module functions."""
import os
import unittest
import yaml
from .base import TempPathTestCase
from containerctl import ConfigError
from containerctl.container import first_file, read_config


class TestContainerFirstFile(TempPathTestCase):
    """container.first_file"""
    def setUp(self):
        TempPathTestCase.setUp(self)
        self.filenames = ['test1', 'test2', 'test3']

    def touch(self, filename):
        filepath = os.path.join(self.path, filename)
        with open(filepath, 'a') as f:
            os.utime(filepath, None)

    def rm(self, filename):
        filepath = os.path.join(self.path, filename)
        if os.path.exists(filepath):
            os.unlink(filepath)

    def test_no_files(self):
        filepath = first_file(self.path, self.filenames)
        self.assertIsNone(filepath)

    def test_one_file(self):
        filename = self.filenames[1]
        self.touch(filename)
        try:

            wantfile = os.path.join(self.path, filename)
            havefile = first_file(self.path, self.filenames)
            self.assertEqual(wantfile, havefile)
        finally:
            self.rm(filename)

    def test_all_files(self):
        try:
            for filename in self.filenames:
                self.touch(filename)

            wantfile = os.path.join(self.path, self.filenames[0])
            havefile = first_file(self.path, self.filenames)
            self.assertEqual(wantfile, havefile)
        finally:
            for filename in self.filenames:
                self.rm(filename)


class TestContainerReadConfig(TempPathTestCase):
    """container.read_config"""
    def setUp(self):
        TempPathTestCase.setUp(self)
        self.filename = 'container.yml'
        self.filepath = os.path.join(self.path, self.filename)

    def write_file(self, data, encode=True):
        """Write ``data`` to the config file. If ``encode`` is ``True`` it will be YAML encoded
        first."""
        if encode:
            data = yaml.dump(data)
        with open(self.filepath, 'w') as f:
            f.write(data)

    def rm_file(self):
        """Unlink the config file."""
        if os.path.exists(self.filepath):
            os.unlink(self.filepath)

    def test_no_file(self):
        self.assertRaises(ConfigError, read_config, self.filepath)

    def test_invalid_data(self):
        self.write_file("this isn't a dictionary!", False)
        try:
            self.assertRaises(ConfigError, read_config, self.filepath)
        finally:
            self.rm_file()

    def test_invalid_yaml(self):
        try:
            self.write_file('yaml:\n  "wut: no', False)
            self.assertRaises(ConfigError, read_config, self.filepath)
        finally:
            self.rm_file()

    def test_no_name(self):
        try:
            self.write_file({'user': 'wifast'})
            self.assertRaises(ConfigError, read_config, self.filepath)
        finally:
            self.rm_file()

    def test_invalid_name(self):
        try:
            self.write_file({'name': {'user': 'user', 'name': 'name'}})
            self.assertRaises(ConfigError, read_config, self.filepath)
        finally:
            self.rm_file()

    def test_invalid_user(self):
        try:
            self.write_file({'name': 'user', 'user': {'wut': 'nope'}})
            self.assertRaises(ConfigError, read_config, self.filepath)
        finally:
            self.rm_file()

    def test_invalid_running(self):
        try:
            self.write_file({'name': 'name', 'running': 'running!'})
            self.assertRaises(ConfigError, read_config, self.filepath)
        finally:
            self.rm_file()

    def test_invalid_testing(self):
        try:
            self.write_file({'name': 'name', 'testing': 'running!'})
            self.assertRaises(ConfigError, read_config, self.filepath)
        finally:
            self.rm_file()

    def test_split_name(self):
        try:
            user = 'user'
            name = 'name'
            self.write_file({'name': '{}/{}'.format(user, name)})
            config = read_config(self.filepath)
            self.assertEqual(user, config.get('user'))
            self.assertEqual(name, config.get('name'))
        finally:
            self.rm_file()
