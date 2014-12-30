# -*- coding: utf-8 -*-

import unittest
import qjson

class qjson_test(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    ## test case, which start with "test_"
    def test_decimal(self):
        self.assertEqual(qjson.loads('{"a":1.7}').a, 1.7, 'test decimal')

    def test_boolean(self):
        self.assertEqual(qjson.loads('{"a":false}').a, False, 'test boolean')
        self.assertEqual(qjson.loads('{"a":true}').a, True, 'test boolean')
    
    def test_null(self):
        self.assertEqual(qjson.loads('{"a":null}').a, None, 'test null')

    def test_array(self):
        self.assertEqual(qjson.loads('["b",1]')[1], 1, 'test array')
        self.assertEqual(qjson.loads('{"a":["b",1]}').a, ["b", 1], 'test array')

    def test_array_has_object(self):
        self.assertEqual(qjson.loads('{"a":["b",{"c": "d"}]}').a[1].c, "d", 'test array with object in it')
    
    def test_string(self):
        self.assertEqual(qjson.loads('{"a":"b"}').a, "b", 'test string')
    
    def test_object(self):
        json_str = '{"person":\
            {"name":"jerry", "age":32, "web":{"url":"http://jatsz.org", "desc":"blog"}}, \
            "grade": "a", "score":[80,90]}'
        info = qjson.loads(json_str)

        self.assertEqual(info.person.name, 'jerry', 'test_object')
        self.assertEqual(info.person.age, 32, 'test_object')
        self.assertEqual(info.person.web.url, "http://jatsz.org", 'test_object')
        self.assertEqual(info.person.web.desc, "blog", 'test_object')

        self.assertEqual(info.grade, "a", 'test_object')
        self.assertEqual(info.score, [80, 90], 'test_object')
        
        
if __name__ =='__main__':
    unittest.main()