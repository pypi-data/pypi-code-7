# coding: utf-8
from __future__ import print_function

from pyjznet import Server
import unittest
import logging


class DemoService(object):
    def sayHi(self, name, remote_service):
        try:
            age = remote_service.call_rpc('demo', 'getAge')
        except Exception as e:
            logging.error(e)
            return str(e)
        logging.info('got say hi request of %s who\'s age is %d' % (name, age))
        return "Hi, %s who's age is %d!" % (name, age)


class TestNetServer(unittest.TestCase):
    def setUp(self):
        pass

    def test_server(self):
        server = Server()
        server.add_rpc_service('demo', DemoService())
        server.start()


if __name__ == '__main__':
    unittest.main()