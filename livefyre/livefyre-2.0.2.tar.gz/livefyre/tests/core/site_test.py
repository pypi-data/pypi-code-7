import unittest

from livefyre import Livefyre
from livefyre.tests import LfTest
from livefyre.src.utils import pyver
from livefyre.src.core.collection.type import CollectionType
from livefyre.src.core.site.model import SiteData
from livefyre.src.core.site import Site


class SiteTestCase(LfTest, unittest.TestCase):
    def test_build_site(self):
        network = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY)
        data = SiteData(self.SITE_ID, self.SITE_KEY)
        
        site = Site(network, data)
        self.assertEquals(network, site.network)
        self.assertEquals(data, site.data)
        
        Site.init(network, self.SITE_ID, self.SITE_KEY)
        if pyver < 2.7:
            pass
        elif pyver < 3.0:
            with self.assertRaisesRegexp(AssertionError, 'id is missing'):
                Site.init(network, None, self.SITE_KEY)
            with self.assertRaisesRegexp(AssertionError, 'key is missing'):
                Site.init(network, self.SITE_ID, None)
        else:
            with self.assertRaisesRegex(AssertionError, 'id is missing'):
                Site.init(network, None, self.SITE_KEY)
            with self.assertRaisesRegex(AssertionError, 'key is missing'):
                Site.init(network, self.SITE_ID, None)
    
    def test_build_collection__fail(self):
        site = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY).get_site(self.SITE_ID, self.SITE_KEY)
        
        if pyver < 2.7:
            pass
        elif pyver < 3.0:
            with self.assertRaisesRegexp(AssertionError, 'url must be a full domain. ie. http://livefyre.com'):
                site.build_comments_collection('title', 'articleId', 'url.com')
            with self.assertRaisesRegexp(AssertionError, 'title\'s length should be under 255 char'):
                site.build_comments_collection('1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456', 'article_id', 'http://url.com')
        else:
            with self.assertRaisesRegex(AssertionError, 'url must be a full domain. ie. http://livefyre.com'):
                site.build_comments_collection('title', 'articleId', 'url.com')
            with self.assertRaisesRegex(AssertionError, 'title\'s length should be under 255 char'):
                site.build_comments_collection('1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456', 'article_id', 'http://url.com')
        
        if pyver >= 2.7:
            with self.assertRaises(AssertionError):
                site.build_collection('bad type', self.TITLE, self.ARTICLE_ID, self.URL)
                
    def test_build_collection_types(self):
        site = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY).get_site(self.SITE_ID, self.SITE_KEY)
        
        collection = site.build_comments_collection(self.TITLE, self.ARTICLE_ID, self.URL)
        self.assertTrue(collection)
        self.assertEquals(collection.data.type, CollectionType.COMMENTS)
        
        collection = site.build_chat_collection(self.TITLE, self.ARTICLE_ID, self.URL)
        self.assertTrue(collection)
        self.assertEquals(collection.data.type, CollectionType.CHAT)
        
        collection = site.build_blog_collection(self.TITLE, self.ARTICLE_ID, self.URL)
        self.assertTrue(collection)
        self.assertEquals(collection.data.type, CollectionType.BLOG)
        
        collection = site.build_counting_collection(self.TITLE, self.ARTICLE_ID, self.URL)
        self.assertTrue(collection)
        self.assertEquals(collection.data.type, CollectionType.COUNTING)
        
        collection = site.build_ratings_collection(self.TITLE, self.ARTICLE_ID, self.URL)
        self.assertTrue(collection)
        self.assertEquals(collection.data.type, CollectionType.RATINGS)

        collection = site.build_reviews_collection(self.TITLE, self.ARTICLE_ID, self.URL)
        self.assertTrue(collection)
        self.assertEquals(collection.data.type, CollectionType.REVIEWS)
        
        collection = site.build_sidenotes_collection(self.TITLE, self.ARTICLE_ID, self.URL)
        self.assertTrue(collection)
        self.assertEquals(collection.data.type, CollectionType.SIDENOTES)
        
        collection = site.build_collection(CollectionType.COMMENTS, self.TITLE, self.ARTICLE_ID, self.URL)
        self.assertTrue(collection)
        self.assertEquals(collection.data.type, CollectionType.COMMENTS)        
        
    def test_get_urn(self):
        site = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY).get_site(self.SITE_ID, self.SITE_KEY)
        
        self.assertEquals(site.network.urn+':site='+self.SITE_ID, site.urn)


if __name__ == '__main__':
    unittest.main()