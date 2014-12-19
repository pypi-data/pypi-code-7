import unittest

from postcodepy_proxy.views import PostcodepyProxyView
from postcodepy_proxy.views import SignalProxyView
from postcodepy_proxy.signalapi import SignalRequestData
from postcodepy import postcodepy

import os, sys
from django.test import Client, RequestFactory
from django.conf import settings
from django.http import HttpResponse
import json


access_key = None
access_secret = None

class TestUM(unittest.TestCase):
    def setUp(self):
      c = Client()
      global access_key
      access_key = os.getenv("ACCESS_KEY")
      global access_secret
      access_secret = os.getenv("ACCESS_SECRET")
      if not (access_key and access_secret ):
        print "provide an access key and secret via environment:"
        print "export ACCESS_KEY=..."
        print "export ACCESS_SECRET=..."
        self.skipTest(self)

class PostcodepyProxyViewTestCase(unittest.TestCase):
  def test_context_data_ValidPostcodeHuisnummer(self):
    """ TEST: execute proxy view to get data for a valid postcode/houseNumber, request should return all data
    """
    requestArgs = { "postcode" : "7514BP", "houseNumber" : 129, "houseNumberAddition" : "" }
    request = RequestFactory().get('/fake-path')
    view = PostcodepyProxyView.as_view()
    response = view(request, **requestArgs)
    #print >>sys.stderr, response
    requestArgs.update({"city" : "Enschede"})
    self.assertEqual(  { "postcode" : response['postcode'], 
                      "houseNumber" : response['houseNumber'],
                             "city" : response['city'],
              "houseNumberAddition" : response['houseNumberAddition'] }, requestArgs )
                          

  def test_context_data_ValidPostcodeHuisnummerWithAddition(self):
    """ TEST: execute proxy view to get data for a valid postcode/houseNumber/houseNumberAddition, request should return all data
    """
    requestArgs = { "postcode" : "7514BP", "houseNumber" : 129, "houseNumberAddition" : "A" }
    request = RequestFactory().get('/fake-path')
    view = PostcodepyProxyView.as_view()
    response = view(request, **requestArgs)
    #print >>sys.stderr, response
    requestArgs.update({"city" : "Enschede"})
    self.assertEqual(  { "postcode" : response['postcode'], 
                      "houseNumber" : response['houseNumber'],
                             "city" : response['city'],
              "houseNumberAddition" : response['houseNumberAddition'] }, requestArgs )


  def test_context_data_InvalidPostcodeHuisnummer(self):
    """ TEST: execute proxy view to get data for a invalid postcode/houseNumber, request should fail with exception
    """
    requestArgs = { "postcode" : "7514BP", "houseNumber" : 129, "houseNumberAddition" : "B" }
    request = RequestFactory().get('/fake-path')
    view = PostcodepyProxyView.as_view()
    with self.assertRaises( postcodepy.PostcodeError) as cm:
      response = view(request, **requestArgs)
      print >>sys.stderr, "ERR", response
      caught_exception = cm.exception
      expected_exception = postcodepy.PostcodeError("ERRHouseNumberAdditionInvalid")
      self.assertEqual( expected_exception.exceptionId, caught_exception.exceptionId)


  def test_context_data_SignalCheckCustomer(self):
    """ TEST: execute proxy view to get data signaldata, request should return JSON with 1 warning, 7 signals
    """
    # The sar (Signal-Api-Request)
    sarArgs = {
        "customer_email": "test-address@postcode.nl",
        "customer_phoneNumber": "+31235325689",
        "customer_address_postcode": "2012ES",
        "customer_address_houseNumber": "30",
        "customer_address_country": "NL",
        "transaction_internalId": "MyID-249084",
        "transaction_deliveryAddress_postcode": "7514BP",
        "transaction_deliveryAddress_houseNumber": "129",
        "transaction_deliveryAddress_houseNumberAddition": "B",
        "transaction_deliveryAddress_country": "NL"
        }
    sar = SignalRequestData(sarArgs)
    sar = sar()
    request = RequestFactory().get('/fake-path')
    view = SignalProxyView.as_view()
    response = view(request, sar=sar)
    #print >>sys.stderr, response
    self.assertEqual( { "warningCount" : response['warningCount'],
                        "lenOfSignalArray" : len(response['signals']), }, 
                      { "warningCount" : 1,
                       "lenOfSignalArray" : 7 } )




if __name__ == "__main__":

  unittest.main()

