import unittest2 as unittest


from ngi.notify.datadog.testing import\
    NGI_NOTIFY_DATADOG_INTEGRATION


class TestExample(unittest.TestCase):

    layer = NGI_NOTIFY_DATADOG_INTEGRATION
    
    def setUp(self):
        # you'll want to use this to set up anything you need for your tests 
        # below
        pass

    def test_success(self):
        sum = 1 + 3
        self.assertEquals(sum, 4)

    def test_failure(self):
        sum = 2 + 3
        self.assertEquals(sum, 4)
