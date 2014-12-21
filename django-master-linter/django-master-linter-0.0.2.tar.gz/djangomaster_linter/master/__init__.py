from djangomaster.conf import settings as master_settings

from djangomaster_linter.master.base import BaseLintView


class PyLintView(BaseLintView):
    name = 'pylint'
    title = 'Py Lint'
    label = 'Py Lint'
    lint_cmd = master_settings.PYLINT_CMD
    lint_is_installed = master_settings.PYLINT_IS_INSTALLED
    conf_name = 'DJANGOMASTER_PYLINT_INGORED_PATTERNS'
    exclude_patterns = master_settings.PYLINT_IGNORED_PATTERNS

    def is_valid_file(self, file_path):
        return file_path.endswith('.py')


class JsLintView(BaseLintView):
    name = 'jslint'
    title = 'JS Lint'
    label = 'JS Lint'
    lint_cmd = master_settings.JSLINT_CMD
    lint_is_installed = master_settings.JSLINT_IS_INSTALLED
    conf_name = 'DJANGOMASTER_JSLINT_INGORED_PATTERNS'
    exclude_patterns = master_settings.JSLINT_IGNORED_PATTERNS

    def is_valid_file(self, file_path):
        return file_path.endswith('.js')
