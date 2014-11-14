from django.test import TestCase
from django.test.client import Client

from models import *
from views import *

import datetime

class ModellTest(TestCase):
    def setUp(self):
        pass

    def test_model_normal(self):
        pass


class DummyRequest:
    def __init__(self,user=None,GET={}):
        self.user=user
        self.GET=GET
        self.POST={}
        self.method="GET"

class ViewTest(TestCase):
    def setUp(self):
        Dispatcher.clear()

    def test_content(self):
        pass



