from pyramid import testing
from webtest import TestApp
from cms import main
from cms.tests.base import UnicoreTestCase


class NotifyTestCase(UnicoreTestCase):

    def setUp(self):
        self.local_workspace = self.mk_workspace(name=self.id().lower())
        self.remote_workspace = self.mk_workspace(
            name='%s_remote' % (self.id().lower(),))

        self.config = testing.setUp()
        settings = {
            'git.path': self.local_workspace.working_dir,
            'git.content_repo_url': self.remote_workspace.working_dir,
            'es.index_prefix': self.local_workspace.index_prefix,
            'CELERY_ALWAYS_EAGER': True
        }
        self.app = TestApp(main({}, **settings))

    def tearDown(self):
        testing.tearDown()

    def test_fastforward(self):
        resp = self.app.get('/api/pages.json', status=200)
        self.assertEquals(len(resp.json), 0)
        resp = self.app.get('/api/categories.json', status=200)
        self.assertEquals(len(resp.json), 0)

        # the remote grows some categories
        self.create_categories(self.remote_workspace)
        self.create_pages(self.remote_workspace)

        local_repo = self.local_workspace.repo
        local_repo.create_remote('origin', self.remote_workspace.working_dir)

        # this should trigger a fastforward
        self.app.post('/api/notify/', status=200)

        resp = self.app.get('/api/pages.json', status=200)
        self.assertEquals(len(resp.json), 2)
        resp = self.app.get('/api/categories.json', status=200)
        self.assertEquals(len(resp.json), 2)
