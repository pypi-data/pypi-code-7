import unittest
from postcodepy import postcodepy

access_key="WY7vmPZN9e0p1W4qdaYKbHyDfL7J94YgbIp2z944oZE"
access_secret="c57Og9t8Lb14A8mHru9BEHwzdoyF7cBqb3xV5rQB4aC"

class TestUM(unittest.TestCase):

    def test_Postcode(self):
      """ test retrieval of data
      """
      api = postcodepy.API( environment='live', access_key=access_key, access_secret=access_secret)
      pc = ('1071XX', 1)
      retValue = api.get_postcodedata( pc[0], pc[1] )
      self.assertEqual( retValue['city'], "Amsterdam" ) and \
            self.assertEqual( retValue['street'], "Museumstraat" ) 

    def test_PostcodeFail(self):
      """ no data for this postcode, a request that should fail 
      """
      api = postcodepy.API( environment='live', access_key=access_key, access_secret=access_secret)
      pc = ('1077XX', 1)
      self.assertRaises( postcodepy.PostcodeError, lambda: api.get_postcodedata( pc[0], pc[1] ))

    def test_SecretFail(self):
      """ no secret : a request that should fail 
      """
      self.assertRaises( postcodepy.PostcodeError,  lambda: postcodepy.API( environment='live', access_key=access_key))

    def test_KeyFail(self):
      """ no key : a request that should fail 
      """
      self.assertRaises( postcodepy.PostcodeError,  lambda: postcodepy.API( environment='live', access_secret=access_secret))

