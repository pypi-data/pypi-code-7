import requests

__author__ = 'oxle019'

from os import path
from fptest.tracing import parse_trace_file

from lxml import etree
import unittest


class FpTest(unittest.TestCase):
    @classmethod
    def zero_file(cls, filename):
        """
        Zero out a file.  Used to clear cartOrderTracing and kpsaOrderTracing before running the tests
        :param filename: File to clear
        """
        with open(filename, 'w'):
            pass

    @classmethod
    def linearize_xml(cls, xml_string):
        """
        Strips insignificant whitespace and adds the xml declaration (unpretty-print)

        This is because FP needs the input to be in this format
        :param xml_string: Pretty-printed xml string
        :return: Headered, unpretty-printed xml string
        """
        parser = etree.XMLParser(remove_blank_text=True)
        elem = etree.XML(xml_string, parser=parser)
        return etree.tostring(elem, xml_declaration=True)

    @classmethod
    def readfile(cls, filename):
        with open(filename, 'r') as f:
            return f.read()

    def __init__(self, *args, **kwargs):
        super(FpTest, self).__init__(*args, **kwargs)
        self.fp_url = 'http://localhost:55000/aff'
        self.fp_node_dir = '../runtime/FPNode'
        self.response = None
        self.cart_order_tracing = None
        self.kpsa_order_tracing = None
        self.fp_response = None
        self.has_run = False

    def request(self):
        """
        Gets the request to post to FP for the test.  There is the helper class method readfile
        :return: XML String of the request
        """
        raise NotImplementedError('The request() method must return the request to send to FP')

    def __do_work(self):
        self.has_run = True
        self.zero_file(path.join(self.fp_node_dir, 'cartOrderTracing.00000.log'))
        self.zero_file(path.join(self.fp_node_dir, 'kpsaOrderTracing.00000.log'))

        data = self.linearize_xml(self.request())
        self.response = requests.post(self.fp_url, data=data)
        self.response.connection.close()
        self.fp_response = etree.XML(self.response.content)
        self.cart_order_tracing = parse_trace_file(path.join(self.fp_node_dir, 'cartOrderTracing.00000.log'))
        self.kpsa_order_tracing = parse_trace_file(path.join(self.fp_node_dir, 'kpsaOrderTracing.00000.log'))

    def setUp(self):
        if not self.has_run:
            self.__do_work()

    def get_fp_status(self):
        """
        Get the execStatus of the response XML
        :return: execStatus
        """
        return self.fp_response.find('execStatus').text

    def get_first_wo(self, wo_name=None):
        """
        Get the first workorder from the list of outgoing work orders in cart_order_tracing
        :param wo_name: Name to query
        :return: Work Order
        """
        if wo_name is None:
            return self.cart_order_tracing.outgoing_workorders[0]
        else:
            return next(wo for wo in self.cart_order_tracing.outgoing_workorders if wo.name == wo_name)
