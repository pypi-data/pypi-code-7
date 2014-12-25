# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
import httpretty

from plcloudclient.tests.v1_0 import utils
from plcloudclient.v1_0 import client


class PlcloudClientTest(utils.TestCase):

    @httpretty.activate
    def test_scoped_init(self):
        self.TEST_URL = 'http://10.0.0.6:5000/v2.0'

        c = client.Client(username='admin',
                          password='admin',
                          tenant_name='admin',
                          auth_url=self.TEST_URL)
        self.assertIsNotNone(c.auth_ref)
        self.assertTrue(c.auth_ref.scoped)
        self.assertTrue(c.auth_ref.project_scoped)
        self.assertFalse(c.auth_ref.domain_scoped)
        self.assertIsNone(c.auth_ref.trust_id)
        self.assertFalse(c.auth_ref.trust_scoped)

    def test_endpoint_init(self):
        c = client.Client(endpoint='endpoint',
                          auth_token='token')
        self.assertIsNotNone(c.auth_ref)
