import re, time, jwt, requests

from livefyre.src.core.site import Site
from livefyre.src.api.domain import Domain
from livefyre.src.utils import pyver
from livefyre.src.exceptions import ApiException
from .model import NetworkData
from .validator import NetworkValidator


class Network(object):
    DEFAULT_USER = 'system'
    DEFAULT_EXPIRES = 86400
    
    def __init__(self, data):
        self.data = data
        self.ssl = True
        
    @staticmethod
    def init(name, key):
        data = NetworkData(name, key)
        return Network(NetworkValidator().validate(data))
    
    def set_user_sync_url(self, url_template):
        assert '{id}' in url_template, 'url_template should have {id}.'
        
        url = Domain.quill(self)+'/'
        data = {'actor_token' : self.build_livefyre_token(), 'pull_profile_url' : url_template}
        headers = {'Content-type': 'application/json'}
        
        response = requests.post(url=url, data=data, headers=headers)
        if response.status_code >= 400:
            raise ApiException(response.status_code)
        
    def sync_user(self, user_id):
        url = '{0}/api/v3_0/user/{1}/refresh'.format(Domain.quill(self), user_id)
        data = {'lftoken' : self.build_livefyre_token()}
        headers = {'Content-type': 'application/json'}
        
        response = requests.post(url=url, data=data, headers=headers)
        if response.status_code >= 400:
            raise ApiException(response.status_code)
        return self
    
    def build_livefyre_token(self):
        return self.build_user_auth_token(self.DEFAULT_USER, self.DEFAULT_USER, self.DEFAULT_EXPIRES)
    
    def build_user_auth_token(self, user_id, display_name, expires):
        assert re.match(r'^[a-zA-Z0-9_\.-]+$', user_id) is not None, 'user_id should only contain alphanumeric characters'
        
        if pyver < 3.0:
            assert isinstance(expires, (int, long, float, complex)), 'expires should be a number'
        else:
            assert isinstance(expires, (int, float, complex)), 'expires should be a number'
            

        token = jwt.encode({
                'domain': self.data.name,
                'user_id': user_id,
                'display_name': display_name,
                'expires': int(time.time()) + expires},
            self.data.key)
        return token.decode('utf-8') if pyver > 3.0 else token
    
    def validate_livefyre_token(self, lf_token):
        token_attr = jwt.decode(lf_token, self.data.key)
        return (token_attr['domain'] == self.data.name
            and token_attr['user_id'] == self.DEFAULT_USER
            and token_attr['expires'] >= int(time.time()))
        
    def get_site(self, site_id, site_key):
        return Site.init(self, site_id, site_key)
    
    @property
    def network_name(self):
        return self.data.name.split('.')[0]
    
    @property
    def urn(self):
        return 'urn:livefyre:' + self.data.name
    
    def get_urn_for_user(self, user):
        return self.urn + ':user=' + user
