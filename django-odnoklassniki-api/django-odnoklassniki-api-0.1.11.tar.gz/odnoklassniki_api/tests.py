# -*- coding: utf-8 -*-
from django.test import TestCase
from utils import api_call

GROUP_ID = 53038939046008


class OdnoklassnikiApiTest(TestCase):

    def test_get_url_info(self):

        response = api_call('url.getInfo', url='http://www.odnoklassniki.ru/apiok')
        self.assertEqual(response, {u'objectId': GROUP_ID, u'type': u'GROUP'})