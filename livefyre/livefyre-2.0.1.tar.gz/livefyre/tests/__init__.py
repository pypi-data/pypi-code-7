from __future__ import print_function

import os, sys
from enum import Enum

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser


class LfTest:
    NETWORK_NAME = '<NETWORK-NAME>'
    NETWORK_KEY = '<NETWORK-KEY>'
    SITE_ID = '<SITE-ID>'
    SITE_KEY = '<SITE-KEY>'
    COLLECTION_ID = '<COLLECTION-ID>'
    USER_ID = '<USER-ID>'
    ARTICLE_ID = '<ARTICLE-ID>'
    TITLE = 'PythonTest'
    URL = 'http://answers.livefyre.com/PYTHON'
    
    def setUp(self):
        self.set_prop_values(LfEnvironments.PROD)
    
    def set_prop_values(self, env):
        config = ConfigParser.RawConfigParser()
        #try loading from file first
        try:
            config.read('test.ini')
        
            self.NETWORK_NAME = config.get(env.value, 'NETWORK_NAME')
            self.NETWORK_KEY = config.get(env.value, 'NETWORK_KEY')
            self.SITE_ID = config.get(env.value, 'SITE_ID')
            self.SITE_KEY = config.get(env.value, 'SITE_KEY')
            self.COLLECTION_ID = config.get(env.value, 'COLLECTION_ID')
            self.USER_ID = config.get(env.value, 'USER_ID')
            self.ARTICLE_ID = config.get(env.value, 'ARTICLE_ID')
            return
        except:
            pass
        
        #next try loading circle ci defaults
        try:
            self.NETWORK_NAME = os.environ.get('NETWORK_NAME')
            self.NETWORK_KEY = os.environ.get('NETWORK_KEY')
            self.SITE_ID = os.environ.get('SITE_ID')
            self.SITE_KEY = os.environ.get('SITE_KEY')
            self.COLLECTION_ID = os.environ.get('COLLECTION_ID')
            self.USER_ID = os.environ.get('USER_ID')
            self.ARTICLE_ID = os.environ.get('ARTICLE_ID')
        except:
            print('no set values have been found!', file=sys.stderr)
        
            
class LfEnvironments(Enum):
    QA = 'qa'
    UAT = 'uat'
    PROD = 'prod'