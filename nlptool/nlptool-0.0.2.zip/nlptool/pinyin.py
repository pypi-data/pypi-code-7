#! /bin/env python
# -*- coding=utf-8 -*-


"""
@Author: darrenwang00@163.com  2014-07-09
@File: pinin.py 
@Version: 1.0.0
@Dep: python2.7
@Brif: 
@Usage: 
"""


from __future__ import unicode_literals
import os.path
import re


class Pinyin(object):
    """
    translate chinese hanzi to pinyin by python
    """

    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'pinyin.dat')

    def __init__(self, data_path=data_path):
        self.pinyin_tone_mark = {
            0: u"aoeiuv\u00fc",
            1: u"\u0101\u014d\u0113\u012b\u016b\u01d6\u01d6",
            2: u"\u00e1\u00f3\u00e9\u00ed\u00fa\u01d8\u01d8",
            3: u"\u01ce\u01d2\u011b\u01d0\u01d4\u01da\u01da",
            4: u"\u00e0\u00f2\u00e8\u00ec\u00f9\u01dc\u01dc",
        }

        self.dict = self.__load_dict(data_path)

    def  __load_dict(self, file_name):
        """
        load  chinese2pinyi dict
        """
        if not os.path.isfile(file_name):
            return {}
        kv_dic = {}
        for line in open(file_name, "r"):
            items = line.strip().split("\t")
            if len(items) == 2:
                kv_dic[items[0]] = items[1].lower()
        return kv_dic

    def get_pinyin(self, uinput_str=u'你好', splitter=u'-', show_tone_marks=False):
        """
        get chinese2pinyi
        """
        result = []
        flag = 1
        for ch in uinput_str:
            key = "%X" % ord(ch)
            if key in self.dict:
                pinyin = self.dict[key]
                first_pinyin = pinyin.split()[0]
                if show_tone_marks:
                    pinyin = self.decode_pinyin(first_pinyin)
                else:
                    pinyin = first_pinyin[:-1]
                result.append(pinyin)
            else:
                if len(result) > 0:
                    result[-1] += ch
                else:
                    result.append(ch)
        return splitter.join(result)

    
    def decode_pinyin(self, input_str):
        """
        Converts text in the numbering format of pinyin 
        eg. ni3hao3 -> nǐhǎo
        """
        s = input_str.lower()
        r = ""
        t = ""
        for c in s:
            if c >= 'a' and c <= 'z':
                t += c
            elif c == ':':
                try:
                    if t[-1] == 'u':
                        t = t[:-1] + u"\u00fc"
                except:
                    pass
            else:
                if c >= '0' and c <= '5':
                    tone = int(c) % 5
                    if tone != 0:
                        m = re.search(u"[aoeiuv\u00fc]+", t)
                        if m is None:
                            t += c
                        elif len(m.group(0)) == 1:
                            t = t[:m.start(0)] + self.pinyin_tone_mark[tone][self.pinyin_tone_mark[0].index(m.group(0))] + t[m.end(0):]
                        else:
                            if 'a' in t:
                                t = t.replace("a", self.pinyin_tone_mark[tone][0])
                            elif 'o' in t:
                                t = t.replace("o", self.pinyin_tone_mark[tone][1])
                            elif 'e' in t:
                                t = t.replace("e", self.pinyin_tone_mark[tone][2])
                            elif t.endswith("ui"):
                                t = t.replace("i", self.pinyin_tone_mark[tone][3])
                            elif t.endswith("iu"):
                                t = t.replace("u", self.pinyin_tone_mark[tone][4])
                            else:
                                t += "!"
                r += t
                t = ""
        r += t
        return r


