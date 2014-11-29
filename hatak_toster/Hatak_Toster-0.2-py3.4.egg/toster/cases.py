from mock import MagicMock

from hatak.unpackrequest import unpack
from toster import TestCase as BaseTestCase


class TestCase(BaseTestCase):

    cache = {}

    def setUp(self):
        super().setUp()
        self.request = MagicMock()
        self.request.registry = {
            'db': MagicMock(),
            'unpacker': self.runner.application.unpacker,
            'settings': {},
            'paths': {},
        }
        unpack(self, self.request)


class ControllerPluginTests(TestCase):

    def setUp(self):
        super().setUp()
        self.controller = MagicMock()
        self.parent = MagicMock()
        self.plugin = self.prefix_from(self.parent, self.controller)


class ModelTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.model = self.prefix_from()


class FormTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.add_mock('CsrfMustMatch', prefix='haplugin.formskit.models.')
        self.form = self.prefix_from(self.request)

    def _create_fake_post(self, data):
        defaults = {
            self.form.form_name_value: [self.form.get_name(), ]
        }
        defaults.update(data)
        self.POST.dict_of_lists.return_value = defaults


class ControllerTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.request.registry['controller_plugins'] = (
            self.runner.application.controller_plugins)
        self.root_tree = MagicMock()
        self.controller = self.prefix_from(self.root_tree, self.request)
        self.data = self.controller.data = {}
        self.matchdict = self.controller.matchdict = {}


class SqlTestCase(TestCase):

    groups = ('sql',)

    def setUp(self):
        super().setUp()
        self.request.db = self.runner.get_db()
        unpack(self, self.request)


class SqlControllerTestCase(ControllerTestCase):

    groups = ('sql',)

    def setUp(self):
        super().setUp()
        self.request.db = self.runner.get_db()
        unpack(self, self.request)
        unpack(self.controller, self.request)
        self.matchdict = self.controller.matchdict = {}


class SqlFormTestCase(FormTestCase):

    groups = ('sql',)

    def setUp(self):
        super().setUp()
        self.request.db = self.runner.get_db()
        unpack(self, self.request)
        unpack(self.form, self.request)


class PluginTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.plugin = self.prefix_from()
        self.app = self.plugin.app = MagicMock()
        self.config = self.app.config
