#! /bin/env python
# -*- coding=utf-8 -*-


"""
@Author: darrenwang00@163.com  2014-07-09
@File: test.py 
@Version: 1.0.0
@Dep: python2.7
@Brif: test
@Usage: just for test
"""


import sys
import unittest

import distance
import pinyin
import simhash


class TestNLPTool(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pinyin(self):
        p = pinyin.Pinyin()
        self.assertEqual(p.get_pinyin(u'上海'), u'shang-hai')
        print u"上海".encode("gb18030"), p.get_pinyin(u'上海',show_tone_marks=True).encode("gb18030")
        print p.get_pinyin(u'Apple发布iOS7', show_tone_marks=True).encode("gb18030")

        #self.assertEqual(p.get_pinyin(u'上海', show_tone_marks=True), u'shàng-hǎi')
        #self.assertTrue(element not in self.seq)

    def test_sim_str(self):
        #self.assertEqual(self.p.get_pinyin(u'上海'), u'shang-hai')
        #self.assertTrue(element not in self.seq)
        print distance.lcs_len(u"agc", u"abc")
        print distance.min_edit_distance(u"agc", u"abc")

    def test_simhash(self):
        s = '看看 哪些 东西 google 最 看重 ？ 标点 ？'
        hash1 = simhash.SimHash(s.split())
        print("0x%x" % hash1.hash)
        
        s = '看看 哪些 东西 google 最 看重 ！ 标点 ！'
        hash2 = simhash.SimHash(s.split())
        print("0x%x" % hash2.hash)
        
        print '%f%% percent similarity on hash' %(100*(hash1.similarity(hash2)))
        print hash1.hamming_distance(hash2),"bits differ out of", hash1.hashbits 


if __name__ == '__main__':
    unittest.main()
    print("done")

