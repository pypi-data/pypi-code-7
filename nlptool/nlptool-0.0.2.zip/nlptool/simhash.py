#! /bin/env python
# -*- coding=utf-8 -*-

"""
@Author: darrenwang00@163.com  2014-07-09
@File: str_sim.py 
@Version: 1.0.0
@Dep: python2.7
@Brif: Implementation of Charikar simhashes in Python
       将比较相似度的文档得到比较相近的 fingerprint
       See: http://dsrg.mff.cuni.cz/~holub/sw/shash/#a1
@Usage: 
"""


#算法介绍如下
g_introduce = '''
simhash算法的输入是一个向量，输出是一个f位的签名值。
为了陈述方便，假设输入的是一个文档的特征集合，每个特征有一定的权重。
比如特征可以是文档中的词，其权重可以是这个词出现的次数。
simhash算法如下：
1、将一个f维的向量V初始化为0；f位的二进制数S初始化为0；
2、对每一个特征：用传统的hash算法对该特征产生一个f位的签名b。对i=1到f：
   如果b的第i位为1，则V的第i个元素加上该特征的权重；
   否则，V的第i个元素减去该特征的权重。  
3、如果V的第i个元素大于0，则S的第i位为1，否则为0；
4、输出S作为签名。
'''


class SimHash():
    def __init__(self, tokens='', hashbits=128):
        self.hashbits = hashbits
        self.hash = self.__simhash(tokens)
    
    def __str__(self):
        return str(self.hash)
 
    def __long__(self):
        return long(self.hash)
 
    def __float__(self):
        return float(self.hash)
 
    def __simhash(self, tokens):
        # Returns a Charikar simhash with appropriate bitlength
        v = [0]*self.hashbits
 
        for t in [self._string_hash(x) for x in tokens]:
            bitmask = 0
            
            for i in range(self.hashbits):
                bitmask = 1 << i
                if t & bitmask:
                    v[i] += 1
                else:
                    v[i] += -1
        fingerprint = 0
        for i in range(self.hashbits):
            if v[i] >= 0:
                fingerprint += 1 << i    
        return fingerprint
    
    def _string_hash(self, v):
        """
            get string hash
        """
        # A variable-length version of Python's builtin hash
        if v == "":
            return 0
        else:
            x = ord(v[0])<<7
            m = 1000003
            mask = 2**self.hashbits-1
            for c in v:
                x = ((x*m)^ord(c)) & mask
            x ^= len(v)
            if x == -1:
                x = -2
            return x
    
    def hamming_distance(self, other_hash):
        """
            get the hamming distance
        """
        x = (self.hash ^ other_hash.hash) & ((1 << self.hashbits) - 1)
        tot = 0
        while x:
            tot += 1
            x &= x-1
        return tot
    
    def similarity(self, other_hash):
        a = float(self.hash)
        b = float(other_hash)
        
        if a > b:
            return b / a
        else:
            return a / b
