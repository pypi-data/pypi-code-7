# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import TestCase

from .models import User

USER_ID = '4'
USER_USERNAME = 'zuck'


class FacebookUsersTest(TestCase):

    def test_fetch_user(self):

        self.assertEqual(User.objects.count(), 0)
        User.remote.fetch(USER_ID)
        User.remote.fetch(USER_USERNAME)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.all()[0]

        self.assertEqual(user.graph_id, USER_ID)
        self.assertEqual(user.name, u'Mark Zuckerberg')
        self.assertEqual(user.first_name, 'Mark')
        self.assertEqual(user.last_name, 'Zuckerberg')
        self.assertEqual(user.link, 'https://www.facebook.com/zuck')
        self.assertEqual(user.username, USER_USERNAME)
        self.assertEqual(user.gender, 'male')
        self.assertEqual(user.locale, 'en_US')
        self.assertTrue(isinstance(user.cover, dict))
        self.assertTrue(isinstance(user.updated_time, datetime))
