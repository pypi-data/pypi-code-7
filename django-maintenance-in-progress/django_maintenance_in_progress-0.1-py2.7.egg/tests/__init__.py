import os
import tempfile

import requests

from django.test.client import Client, RequestFactory
from django.test import LiveServerTestCase

from maintenance_in_progress.models import Preferences


class TestCase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestCase, cls).setUpClass()
        cls.fpath = os.path.join(tempfile.gettempdir(), "mip-marker")

    def tearDownTest(self):
        # Reset to defaults
        p = Preferences.objects.get()
        p.in_progress = False
        p.file_marker = None
        p.save()

        if os.path.exists(self.fpath):
            os.path.unlink(self.fpath)

        super(TestCase, self).tearDownTest()

    def test_normal_500(self):
        response = requests.get("%s/mip-error/" % self.live_server_url)
        self.assertEqual(response.status_code, 500)

    def test_migration_db_500(self):
        p = Preferences.objects.get()
        p.in_progress = True
        p.save()
        response = requests.get("%s/mip-error/" % self.live_server_url)
        self.assertEqual(response.status_code, 200)

    def test_migration_file_500(self):
        fp = open(self.fpath, "w")
        fp.write("x")
        fp.close()
        p = Preferences.objects.get()
        p.file_marker = self.fpath
        p.save()
        response = requests.get("%s/mip-error/" % self.live_server_url)
        self.assertEqual(response.status_code, 200)
