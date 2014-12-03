import unittest, datetime

from livefyre import Livefyre
from livefyre.tests import LfTest
from livefyre.src.api.personalizedstream import PersonalizedStream
from livefyre.src.cursor.model import CursorData
from livefyre.src.cursor import TimelineCursor


class PersonalizedStreamsTestCase(LfTest, unittest.TestCase):
    def setUp(self):
        super(PersonalizedStreamsTestCase, self).setUp()
        self.network = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY)
        self.site = self.network.get_site(self.SITE_ID, self.SITE_KEY)
        

    def test_network_topic(self):
        topic = PersonalizedStream.create_or_update_topic(self.network, '1', 'UN')
        t = PersonalizedStream.get_topic(self.network, 1)
        self.assertTrue(t)
        self.assertEqual(t.label, topic.label)
        
        self.assertTrue(PersonalizedStream.delete_topic(self.network, topic))
    
    def test_network_topics(self):
        topic_dict = {'1': 'UN', '2': 'DEUX'}
        topics = PersonalizedStream.create_or_update_topics(self.network, topic_dict)
        self.assertEqual(2, len(topics))
        
        returned_topics = PersonalizedStream.get_topics(self.network, 1, 0)
        self.assertEqual(1, len(returned_topics))
        
        deleted = PersonalizedStream.delete_topics(self.network, topics)
        self.assertEqual(len(topics), deleted)
     
    def test_site_topic(self):
        topic = PersonalizedStream.create_or_update_topic(self.site, '2', 'DEUX')
        
        t = PersonalizedStream.get_topic(self.site, 2)
        self.assertTrue(t)
        self.assertEqual(t.label, topic.label)
        
        self.assertTrue(PersonalizedStream.delete_topic(self.site, topic))
     
    def test_site_topics(self):
        topic_dict = {'1': 'UN', '2': 'DEUX'}
        topics = PersonalizedStream.create_or_update_topics(self.site, topic_dict)
        self.assertEqual(2, len(topics))
        
        returned_topics = PersonalizedStream.get_topics(self.site, 1, 0)
        self.assertEqual(1, len(returned_topics))
        
        deleted = PersonalizedStream.delete_topics(self.site, topics)
        self.assertEqual(len(topics), deleted)
      
    def test_collection_topics__network(self):
        topic_dict = {'1': 'UN', '2': 'DEUX'}
        topics = PersonalizedStream.create_or_update_topics(self.network, topic_dict)
        collection_name = 'PYTHON PSSTREAM TEST ' + str(datetime.datetime.now())
        collection = self.site.build_comments_collection(collection_name, collection_name, self.URL).create_or_update()
        
        topic_ids = PersonalizedStream.get_collection_topics(collection)
        self.assertFalse(topic_ids)
            
        added = PersonalizedStream.add_collection_topics(collection, topics)
        self.assertEqual(2, added)
        
        added, removed = PersonalizedStream.replace_collection_topics(collection, [topics[0]])
        self.assertTrue(added > 0 or removed > 0)
        
        removed = PersonalizedStream.remove_collection_topics(collection, [topics[0]])
        self.assertEqual(1, removed)
        
        collection_topics = PersonalizedStream.get_collection_topics(collection)
        self.assertFalse(collection_topics)
        
        collection_name = 'PYTHON PSSTREAM TEST ' + str(datetime.datetime.now())
        collection = self.site.build_comments_collection(collection_name, collection_name, self.URL)
        collection.data.topics = topics
        collection.create_or_update()
            
        PersonalizedStream.delete_topics(self.site, topics) 
    
    def test_collection_topics__site(self):
        topic_dict = {'1': 'UN', '2': 'DEUX'}
        topics = PersonalizedStream.create_or_update_topics(self.site, topic_dict)
        collection_name = 'PYTHON PSSTREAM TEST ' + str(datetime.datetime.now())
        collection = self.site.build_comments_collection(collection_name, collection_name, self.URL).create_or_update()
        
        topic_ids = PersonalizedStream.get_collection_topics(collection)
        self.assertFalse(topic_ids)
            
        added = PersonalizedStream.add_collection_topics(collection, topics)
        self.assertEqual(2, added)
        
        added, removed = PersonalizedStream.replace_collection_topics(collection, [topics[0]])
        self.assertTrue(added == 0 and removed == 1)
        
        removed = PersonalizedStream.remove_collection_topics(collection, [topics[0]])
        self.assertEqual(1, removed)
        
        collection_topics = PersonalizedStream.get_collection_topics(collection)
        self.assertFalse(collection_topics)
        
        collection_name = 'PYTHON PSSTREAM TEST ' + str(datetime.datetime.now())
        collection = self.site.build_comments_collection(collection_name, collection_name, self.URL)
        collection.data.topics = topics
        collection.create_or_update()
            
        PersonalizedStream.delete_topics(self.site, topics)
      
    def test_subscription_api(self):
        user_token = self.network.build_user_auth_token(self.USER_ID, self.USER_ID + '@' + self.NETWORK_NAME, self.network.DEFAULT_EXPIRES)
        topic_dict = {'1': 'UN', '2': 'DEUX'}
        topics = PersonalizedStream.create_or_update_topics(self.network, topic_dict)
        
        subs = PersonalizedStream.get_subscriptions(self.network, self.USER_ID)
        self.assertFalse(subs)
        
        added = PersonalizedStream.add_subscriptions(self.network, user_token, topics)
        self.assertTrue(2, added)
        
        subs = PersonalizedStream.get_subscriptions(self.network, self.USER_ID)
        self.assertTrue(2, len(subs))
        
        added, removed = PersonalizedStream.replace_subscriptions(self.network, user_token, [topics[1]])
        self.assertTrue(added == 0 and removed == 1)
        
        user_subs = PersonalizedStream.get_subscribers(self.network, topics[1])
        self.assertEqual(1, len(user_subs))
        
        removed = PersonalizedStream.remove_subscriptions(self.network, user_token, [topics[1]])
        self.assertEqual(1, removed)
        
        subs = PersonalizedStream.get_subscriptions(self.network, self.USER_ID)
        self.assertFalse(subs)
           
        PersonalizedStream.delete_topics(self.network, topics)
      
    def test_timeline_cursor(self):
        topic = PersonalizedStream.create_or_update_topic(self.network, '1', 'UN')
        cursor = TimelineCursor.init(self.network, topic.topic_id +":topicStream", 50, datetime.datetime.now())
        
        data = PersonalizedStream.get_timeline_stream(cursor, True)
        self.assertTrue(data)
        
        PersonalizedStream.delete_topic(self.network, topic)
  
        
if __name__ == '__main__':
    unittest.main()