# -*- coding: utf-8 -*-

from django.test import Client, TestCase


class SmartProxyTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    def test_proxy_not_configured(self):
        response = self.client.get('/does_not_exist/')
