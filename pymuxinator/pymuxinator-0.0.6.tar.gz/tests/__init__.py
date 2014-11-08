import os

from unittest import TestCase
from pymuxinator import config

class FixturedTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        config.root = os.path.dirname(__file__) + '/fixtures/'

        super(FixturedTestCase, self).__init__(*args, **kwargs)
