import unittest

from livefyre.tests import LfTest
from livefyre.src.dto.topic import Topic
from livefyre import Livefyre

try:
    import simplejson as json
except ImportError:
    import json


class TopicTestCase(LfTest, unittest.TestCase):
    ID = 'id'
    LABEL = 'label'
    CREATED_AT = 10
    MODIFIED_AT = 100
    DICT = {'id': ID, 'label': LABEL, 'createdAt': CREATED_AT, 'modifiedAt': MODIFIED_AT}
    
    def test_init(self):
        topic = Topic(self.ID, self.LABEL, self.CREATED_AT, self.MODIFIED_AT)
        self.assertEqual(self.ID, topic.topic_id)
        self.assertEqual(self.LABEL, topic.label)
        self.assertEqual(self.CREATED_AT, topic.created_at)
        self.assertEqual(self.MODIFIED_AT, topic.modified_at)
        
    def test_func(self):
        topic = Topic(self.ID, self.LABEL, self.CREATED_AT, self.MODIFIED_AT)
        self.assertEqual(self.DICT, topic.to_dict())
        
        topic2 = Topic.serialize_from_json(self.DICT)
        self.assertEqual(self.ID, topic2.topic_id)
        self.assertEqual(self.LABEL, topic2.label)
        self.assertEqual(self.CREATED_AT, topic2.created_at)
        self.assertEqual(self.MODIFIED_AT, topic2.modified_at)
        
        topic3 = json.dumps(topic2)
        self.assertEqual(json.dumps(self.DICT), topic3)
        
        topic = topic.create(Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY), 'ID', 'LABEL')
        self.assertEqual(topic.truncated_id, 'ID')
        
        
if __name__ == '__main__':
    unittest.main()
