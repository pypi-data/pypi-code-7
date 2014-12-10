import unittest
 
from livefyre import Livefyre
from livefyre.tests import LfTest
from livefyre.src.utils import pyver
from livefyre.src.core.network import Network
from livefyre.src.core.network.model import NetworkData
 
 
class NetworkTestCase(LfTest, unittest.TestCase):
    def test_build_network(self):
        network = Network(NetworkData(self.NETWORK_NAME, self.NETWORK_KEY))
        self.assertEquals(network.data.name, self.NETWORK_NAME)
        self.assertEquals(network.data.key, self.NETWORK_KEY)
        self.assertEquals(network.network_name, self.NETWORK_NAME.split('.')[0])
        
        if pyver < 2.7:
            pass
        elif pyver < 3.0:
            with self.assertRaisesRegexp(AssertionError, 'name is missing'):
                Network.init(None, self.NETWORK_KEY)
            with self.assertRaisesRegexp(AssertionError, 'key is missing'):
                Network.init(self.NETWORK_NAME, None)
            with self.assertRaisesRegexp(AssertionError, 'name must end with \'fyre.co\''):
                Network.init('network.name', self.NETWORK_KEY)
        else:
            with self.assertRaisesRegex(AssertionError, 'name is missing'):
                Network.init(None, self.NETWORK_KEY)
            with self.assertRaisesRegex(AssertionError, 'key is missing'):
                Network.init(self.NETWORK_NAME, None)
            with self.assertRaisesRegex(AssertionError, 'name must end with \'fyre.co\''):
                Network.init('network.name', self.NETWORK_KEY)
        
        
    def test_urn(self):
        network = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY)
        self.assertEquals('urn:livefyre:'+self.NETWORK_NAME, network.urn)
        
        self.assertEquals(network.urn+':user='+self.USER_ID, network.get_urn_for_user(self.USER_ID))
        
        
    def test_set_user_sync_url(self):
        network = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY)
         
        if pyver < 2.7:
            pass
        elif pyver < 3.0: 
            with self.assertRaisesRegexp(AssertionError, 'url_template should have {id}.'):
                network.set_user_sync_url('http://thisisa.test.url/')
        else:
            with self.assertRaisesRegex(AssertionError, 'url_template should have {id}.'):
                network.set_user_sync_url('http://thisisa.test.url/')
             
        network.set_user_sync_url('http://answers.livefyre.com/{id}')
        network.sync_user('user')
     
    def test_build_validate_user_token(self):
        network = Livefyre.get_network(self.NETWORK_NAME, self.NETWORK_KEY)
         
        if pyver < 2.7:
            pass
        elif pyver < 3.0:
            with self.assertRaisesRegexp(AssertionError, 'user_id should only contain alphanumeric characters'):
                network.build_user_auth_token('system@blah', 'testName', 86400.0)
            with self.assertRaisesRegexp(AssertionError, 'expires should be a number'):
                network.build_user_auth_token('blah', 'blah', '100')
            
        else:
            with self.assertRaisesRegex(AssertionError, 'user_id should only contain alphanumeric characters'):
                network.build_user_auth_token('system@blah', 'testName', 86400.0)
            with self.assertRaisesRegex(AssertionError, 'expires should be a number'):
                network.build_user_auth_token('blah', 'blah', '100')
         
        token = network.build_livefyre_token()
         
        self.assertTrue(token)
        self.assertTrue(network.validate_livefyre_token(token))
         
         
if __name__ == '__main__':
    unittest.main()