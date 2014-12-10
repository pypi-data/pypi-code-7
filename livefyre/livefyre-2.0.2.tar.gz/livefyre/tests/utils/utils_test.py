# coding: utf-8

import unittest

from livefyre.src.utils import is_valid_full_url


class UtilsTestCase(unittest.TestCase):
    def test_validate_url(self):
        self.assertFalse(is_valid_full_url("test.com"))
        
        self.assertTrue(is_valid_full_url("http://test.com:8000"))
        self.assertTrue(is_valid_full_url("http://test.com"))
        self.assertTrue(is_valid_full_url("https://test.com/"))
        self.assertTrue(is_valid_full_url("ftp://test.com/"))
        self.assertTrue(is_valid_full_url("http://清华大学.cn"))
        self.assertTrue(is_valid_full_url("http://www.mysite.com/myresumé.html"))
        self.assertTrue(is_valid_full_url("https://test.com/path/test.-_~!$&'()*+,=:@/dash"))


    #need more util tests
        
if __name__ == '__main__':
    unittest.main()