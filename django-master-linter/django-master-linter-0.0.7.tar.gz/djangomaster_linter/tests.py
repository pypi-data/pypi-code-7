import os

from django.test import TestCase, override_settings

from test_settings import BASE_DIR
from djangomaster_linter.master import PyLintView, JsLintView
from djangomaster_linter.master.base import _is_installed, Result, BaseLintView


class TestFunctions(TestCase):

    def test__is_installed(self):
        result = _is_installed('ls')
        self.assertTrue(result)

        result = _is_installed('fakecommand')
        self.assertFalse(result)


class TestResult(TestCase):

    @override_settings(BASE_DIR='/path/to')
    def test_init(self):
        result = Result('/path/to/file.py', 'echo')

        self.assertEqual(result._path, '/path/to/file.py')
        self.assertEqual(result._cmd, 'echo')
        self.assertEqual(result._result, '')

        # properties
        self.assertEqual(result.filename, 'file.py')
        result._result = 'something'
        self.assertEqual(result.result, 'something')

    def test_execute(self):
        result = Result('/path/to/file.py', 'echo')

        cmd_result = result.execute()
        self.assertEqual(cmd_result, '/path/to/file.py\n')
        self.assertEqual(result.result, '/path/to/file.py\n')


class TestBaseLintView(TestCase):

    def setUp(self):
        self.base = BaseLintView()

    def test_is_lint_installed(self):
        self.base.lint_cmd = 'ls'
        self.assertTrue(self.base.is_lint_installed())

        self.base.lint_cmd = 'fakecommand'
        self.assertFalse(self.base.is_lint_installed())

    def test_is_valid_file(self):
        self.assertTrue(self.base.is_valid_file('/path/to/file.py'))

    def test_lint(self):
        self.base.lint_cmd = 'echo'
        result = self.base.lint('/path/to/file.py')
        self.assertIsInstance(result, Result)
        self.assertEqual(result._cmd, 'echo')

    def test_get_app_dirs(self):
        dirs = self.base.get_app_dirs()
        res = dirs[-1].endswith('django-master-linter/djangomaster_linter')
        self.assertTrue(res)

    def test_get_files(self):
        base_dir = os.path.join(BASE_DIR, 'djangomaster_linter', 'master')
        self.base.exclude_patterns = (r'base\.py$', )

        for result in self.base.get_files(base_dir):
            self.assertIsInstance(result, Result)
            self.assertFalse(result._path.endswith('base.py'))

    def test_get_queryset(self):
        with override_settings(BASE_DIR=None):
            self.assertEqual(self.base.get_queryset(), [])

        results = self.base.get_queryset()
        for result in results:
            self.assertIsInstance(result, Result)

    def test_get_context_data(self):
        keys = ('page_title', 'LINT_IS_INSTALLED', 'LINT_CMD',
                'ignored_patterns', 'conf_name')
        self.base.lint_cmd = 'ls'
        context = self.base.get_context_data()
        for key in keys:
            self.assertIn(key, context)


class TestPyLintView(TestCase):

    def test_is_valid_file(self):
        linter = PyLintView()
        self.assertTrue(linter.is_valid_file('/path/to/file.py'))
        self.assertFalse(linter.is_valid_file('/path/to/file.js'))


class TestJsLintView(TestCase):

    def test_is_valid_file(self):
        linter = JsLintView()
        self.assertTrue(linter.is_valid_file('/path/to/file.js'))
        self.assertFalse(linter.is_valid_file('/path/to/file.py'))
