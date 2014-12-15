# -*- coding: UTF-8 -*-
from .suite import BaseTestSuite


class TestSite(BaseTestSuite):
    def test_index(self):
        res = self.client.get('/')
        assert res.status_code == 200