import os
import os.path
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from test import httpd


class QuteTestCase(unittest.TestCase):

    def __init__(self, commands):
        super().__init__()
        self.commands = commands

    def setUp(self):
        http.urls = []

    def tearDown(self):
        pass

    def runTest(self):
        print(self.commands)


def collect_tests():
    return [QuteTestCase('foo')]


def main():
    httpd.start_server()
    suite = unittest.TestSuite()
    tests = collect_tests()
    suite.addTests(tests)
    unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    main()
