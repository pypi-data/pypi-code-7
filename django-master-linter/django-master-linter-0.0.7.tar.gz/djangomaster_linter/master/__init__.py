from djangomaster.conf import settings

from djangomaster_linter.master.base import BaseLintView


PYLINT_CMD = settings.get('PYLINT_CMD', 'pylint')
PYLINT_IGNORE_PATTERNS = settings.get('PYLINT_IGNORE_PATTERNS',
                                      (r'/migrations/', ))

JSLINT_CMD = settings.get('JSLINT_CMD', 'jshint')
JSLINT_IGNORE_PATTERNS = settings.get('JSLINT_IGNORE_PATTERNS',
                                      (r'/node_modules/',
                                       r'/bower_components', ))


class PyLintView(BaseLintView):
    abstract = False
    name = 'pylint'
    title = 'Py Lint'
    label = 'Py Lint'
    lint_cmd = PYLINT_CMD
    exclude_patterns = PYLINT_IGNORE_PATTERNS
    conf_name = 'DJANGOMASTER_PYLINT_INGORED_PATTERNS'

    def is_valid_file(self, file_path):
        return file_path.endswith('.py')


class JsLintView(BaseLintView):
    abstract = False
    name = 'jslint'
    title = 'JS Lint'
    label = 'JS Lint'
    lint_cmd = JSLINT_CMD
    exclude_patterns = JSLINT_IGNORE_PATTERNS
    conf_name = 'DJANGOMASTER_JSLINT_INGORED_PATTERNS'

    def is_valid_file(self, file_path):
        return file_path.endswith('.js')
