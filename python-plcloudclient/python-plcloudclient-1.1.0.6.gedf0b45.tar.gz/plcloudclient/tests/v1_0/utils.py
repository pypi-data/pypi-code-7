# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
import os

from keystoneclient.tests import utils

from plcloudclient.v1_0 import client


class TestCase(utils.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()

        self.username = os.environ.get('OS_USERNAME')
        self.password = os.environ.get('OS_PASSWORD')
        self.auth_url = os.environ.get('OS_AUTH_URL')
        self.tenant_name = os.environ.get('OS_TENANT_NAME')
        self.region_name = os.environ.get('OS_REGION_NAME')
        self.endpoint = os.environ.get('PLCLOUD_SERVICE_ENDPOINT')
        self.token = os.environ.get('OS_TOKEN')

        if self.endpoint:
            self.client = client.Client(endpoint=self.endpoint,
                                        token=self.token)
        else:
            self.client = client.Client(username=self.username,
                                        password=self.password,
                                        tenant_name=self.tenant_name,
                                        auth_url=self.auth_url)
