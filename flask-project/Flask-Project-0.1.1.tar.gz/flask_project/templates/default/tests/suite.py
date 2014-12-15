from __future__ import unicode_literals
from web_site import db, create_app


class BaseTestSuite(object):
    def setup(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def teardown(self):
        with self.app.app_context():
            db.drop_all()
