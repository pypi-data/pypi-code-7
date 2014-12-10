from livefyre.src.core.collection import Collection
from livefyre.src.core.collection.type import CollectionType
from .model import SiteData
from .validator import SiteValidator

class Site(object):
    def __init__(self, network, data):
        self.network = network
        self.data = data
        
    @staticmethod
    def init(network, site_id, key):
        data = SiteData(site_id, key)
        return Site(network, SiteValidator().validate(data))
    
    def build_comments_collection(self, title, article_id, url):
        return self.build_collection(CollectionType.COMMENTS, title, article_id, url)
    
    def build_blog_collection(self, title, article_id, url):
        return self.build_collection(CollectionType.BLOG, title, article_id, url)
        
    def build_chat_collection(self, title, article_id, url):
        return self.build_collection(CollectionType.CHAT, title, article_id, url)
    
    def build_counting_collection(self, title, article_id, url):
        return self.build_collection(CollectionType.COUNTING, title, article_id, url)
    
    def build_ratings_collection(self, title, article_id, url):
        return self.build_collection(CollectionType.RATINGS, title, article_id, url)
    
    def build_reviews_collection(self, title, article_id, url):
        return self.build_collection(CollectionType.REVIEWS, title, article_id, url)
    
    def build_sidenotes_collection(self, title, article_id, url):
        return self.build_collection(CollectionType.SIDENOTES, title, article_id, url)
    
    def build_collection(self, ctype, title, article_id, url):
        return Collection.init(self, ctype, title, article_id, url)
    
    @property
    def urn(self):
        return self.network.urn + ':site=' + self.data.id
