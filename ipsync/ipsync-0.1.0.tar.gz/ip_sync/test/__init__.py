# pylint: disable=C0111,R0903
"""Tests for the ip_sync package."""
import unittest
import six
import io
import yaml


class TestBase(unittest.TestCase):

    """Base class to provide configuration data to all unit tests."""

    def setUp(self):
        """Setup the unit test."""
        self._config_yaml = six.u("""rackspace:
  api_username: test
  api_key: 123abc
  domains:
    - test.com
    - www.test.com

namecheap:
  test.com:
    hostname: www
    password: password

  example.com:
    hostname: test
    password: 123456""")

        self._config_data = yaml.safe_load(self._config_yaml)

        self._config_file = io.StringIO(self._config_yaml)
        self._config_file.name = 'test_config.yml'

        self._args = {
            '--config': self._config_file,
            '--dry-run': False,
            '--help': False,
            '--version': False,
            '<command>': 'update'}
