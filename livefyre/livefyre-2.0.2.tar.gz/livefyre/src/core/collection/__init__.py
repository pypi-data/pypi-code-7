import base64, hashlib
import jwt, requests

from livefyre.src.utils import is_valid_full_url, pyver
from livefyre.src.api.domain import Domain
from livefyre.src.exceptions import LivefyreException, ApiException
from .model import CollectionData
from .validator import CollectionValidator

try:
    import simplejson as json
except ImportError:
    import json


class Collection(object):
    def __init__(self, site, data):
        self.site = site
        self.data = data
        
    @staticmethod
    def init(site, ctype, title, article_id, url):
        data = CollectionData(ctype, title, article_id, url)
        return Collection(site, CollectionValidator().validate(data))
    
    def create_or_update(self):
        response = self.__invoke_collection_api('create')
        if response.status_code == 200:
            self.data.id = response.json()['data']['collectionId']
            return self
        if response.status_code == 409:
            response = self.__invoke_collection_api('update')
            if response.status_code == 200:
                self.data.id = response.json()['data']['collectionId']
                return self
        raise ApiException(response.status_code)

    def build_collection_meta_token(self):
        j = self.data.as_map()
        j['iss'] = self.site.network.urn if self.is_network_issued() else self.site.urn
        
        token = jwt.encode(j, self.site.network.data.key if self.is_network_issued() else self.site.data.key)
        return token.decode('utf-8') if pyver > 3.0 else token
    
    def build_checksum(self):
        json_string = json.dumps(self.data.as_map(), sort_keys=True, separators=(',',':'))
        return hashlib.md5(json_string.encode('utf-8')).hexdigest()
    
    def get_collection_content(self):
        if pyver >= 3.0:
            article_bytes = str(self.data.article_id).encode('utf-8')
        else:
            article_bytes = bytes(str(self.data.article_id))
        encoded_article_id = base64.b64encode(article_bytes).decode('utf-8')
        url = '{0}/bs3/{1}/{2}/{3}/init'.format(Domain.bootstrap(self), self.site.network.data.name, self.site.data.id, encoded_article_id)
        
        response = requests.get(url=url)
        if response.status_code <= 400:
            return response.json()
        raise ApiException(response.status_code)

    @property
    def urn(self):
        return self.site.urn + ':collection=' + self.data.id
    
    def is_network_issued(self):
        topics = getattr(self.data, 'topics', None)
        if topics:
            network_urn = self.site.network.urn
            for topic in topics:
                try:
                    topic_id = topic.topic_id
                    if topic_id.startswith(network_urn) and not topic_id.replace(network_urn, '?', 1).startswith(':site='):
                        return True
                except AttributeError:
                    raise LivefyreException('Collection attribute topics should be a list of Topic objects!')
        return False

    def __invoke_collection_api(self, method):
        uri = '{0}/api/v3.0/site/{1}/collection/{2}/'.format(Domain.quill(self), self.site.data.id, method)
        data = self.__get_payload()
        headers = {'Content-Type': 'application/json', 'Accepts': 'application/json'}
            
        response = requests.post(uri, params={'sync':1}, data=json.dumps(data), headers=headers)
        return response
    
    def __get_payload(self):
        return {
            'articleId': self.data.article_id,
            'collectionMeta': self.build_collection_meta_token(),
            'checksum': self.build_checksum(),
        }
