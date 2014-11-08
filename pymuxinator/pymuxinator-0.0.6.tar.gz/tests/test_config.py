import mock

from jinja2 import Template
from pymuxinator import config, exceptions
from tests import FixturedTestCase
from unittest import TestCase


class TestListAll(FixturedTestCase):
    def test_list(self):
        configs = config.list_all()

        # strip root directory out of path names
        configs = [c.replace(config.root, '') for c in configs]

        # make sure it walks the file tree
        self.assertIn('sample.yml', configs)
        self.assertIn('level1/one.yml', configs)
        self.assertIn('level1/level2/two.yml', configs)

    def test_bad_root_path(self):
        # mock config
        old_value = config.root
        config.root = 'dasfjaskldaj'

        # make sure it doesn't error
        self.assertEqual(config.list_all(), [])

        # reset config
        config.root = old_value


class TestProjectPath(FixturedTestCase):
    def test_existing_path(self):
        expected = config.root + 'sample.yml'
        self.assertEqual(config.project_path('sample'), expected)

    def test_non_existing_path(self):
        with self.assertRaises(exceptions.ProjectNotFoundError):
            config.project_path('foobarrr')


class TestLoad(FixturedTestCase):
    def test_load(self):
        """Sanity check that it loads the YAML from the file"""
        sample = config.load('sample')
        self.assertEqual(sample['root'], '~/test')

    def test_load_parse_error(self):
        with self.assertRaises(exceptions.ConfigParseError):
            config.load('bad_syntax')


class TestLoadTemplate(TestCase):
    def test_load(self):
        """Make sure the template is loaded correctly"""
        template = config.load_template('tmux')
        self.assertTrue(isinstance(template, Template))


class TestGetEnvVar(TestCase):
    @mock.patch('os.environ.get', return_value='foo')
    def test_get(self, mock_get):
        self.assertEqual(config.get_env_var('HOME'), 'foo')

    @mock.patch('os.environ.get')
    def test_get_default(self, mock_get):
        config.get_env_var('HOME', 'testing')
        mock_get.assert_called_once_with('HOME', 'testing')
