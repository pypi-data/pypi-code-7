import unittest

from postcodepy_proxy.views import PostcodepyProxyView
from postcodepy import postcodepy

import os, sys
from django.test import Client, RequestFactory
from django.conf import settings


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



if __name__ == "__main__":

  unittest.main()

