import unittest

from livefyre.tests import LfTest
from livefyre.src.dto.subscription import Subscription, SubscriptionType

try:
    import simplejson as json
except ImportError:
    import json


class SubscriptionTestCase(LfTest, unittest.TestCase):
    TO = 'to'
    BY = 'by'
    TYPE = SubscriptionType.personalStream
    CREATED_AT = 10
    DICT = {'to': TO, 'by': BY, 'type': TYPE.name, 'createdAt': CREATED_AT}
    
    def test_init(self):
        sub = Subscription(self.TO, self.BY, self.TYPE, self.CREATED_AT)
        self.assertEqual(self.TO, sub.to)
        self.assertEqual(self.BY, sub.by)
        self.assertEqual(self.TYPE, sub.sub_type)
        self.assertEqual(self.CREATED_AT, sub.created_at)
        
    def test_func(self):
        sub = Subscription(self.TO, self.BY, self.TYPE, self.CREATED_AT)
        self.assertEqual(self.DICT, sub.to_dict())
        
        sub2 = Subscription.serialize_from_json(self.DICT)
        self.assertEqual(self.TO, sub2.to)
        self.assertEqual(self.BY, sub2.by)
        self.assertEqual(self.TYPE, sub2.sub_type)
        self.assertEqual(self.CREATED_AT, sub2.created_at)
        
        sub3 = json.dumps(sub2)
        self.assertEqual(json.dumps(self.DICT), sub3)
        
        
if __name__ == '__main__':
    unittest.main()
