import unittest
import beans
import logging
# Create your tests here.

# TODO: Add error logger test

# ENDPOINT = 'http://api.lvho.st/v1/'
ENDPOINT = 'http://api.test.beans.cards/v1/'


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.secret_good = 'sk_0w9P2An1u7LDPjxbnvC7wpff'
        self.secret_bad = 'sk_0w9P2An1u7LDPjxbnvC7wpff5'

        self.public_good = 'bsn_07mnkjb7d4wM'
        # self.public_bad = 'bsn_07mnkjb7d4wM5';

        self.acc_good = 'acc_0N2Qqw5nInMu'
        # self.acc_bad = 'acc_0N2Qqw5nInMu5'

        self.rt_ccy_spent = 'rt_09uk'

        self.sdk_version = '1.2'

        beans.init(self.secret_good, fail_silently=True, signature='Regression Test')
        beans.default.endpoint = ENDPOINT

    # Check the Version on the SDK
    def test_version(self):
        self.assertTrue(beans.__version__ == self.sdk_version)

    # Testing secret keys
    def test_keys(self):
        self.assertIsInstance(beans.get('business/'+self.public_good), dict)
        beans.default.__secret__ = self.secret_bad
        self.assertRaises(beans.BeansException, beans.get, path='business'+self.public_good)
        beans.default.__secret__ = self.secret_good

    #Testing robustest
    def test_robustest(self):
        self.assertIsInstance(beans.get('business/'+self.public_good), dict)
        self.assertIsInstance(beans.get('business/'+self.public_good+'/'), dict)
        self.assertIsInstance(beans.get('currency/iso', iso='USD'), dict)
        self.assertRaises(beans.BeansException, beans.get, path='foo')

    # def test_logger(self):
    #
    #     beans.default.fail_silently = True
    #     beans.default.logger = logging.Logger('beans_test')
    #     cookies = {'beans_user': 'anonymous'}
    #     beans.get_token_from_cookie(cookies=cookies)

if __name__ == '__main__':
    unittest.main()