#! /bin/env python
# -*- coding=utf-8 -*-

"""
@Author: darrenwang00@163.com  2014-07-09
@File: str_sim.py 
@Version: 1.0.0
@Dep: python2.7
@Brif: 
@Usage: 
"""

import math
import copy
import sys


def lcs_len(ustring1, ustring2):
    """
    Longest Common Substring
    Args:
        ustring1 (unicode): str1
        ustring2 (unicode): str2
    Returns:
        len(lcs)
    """
    if (u"" == ustring1 or u"" == ustring2):
        return 0
    length1 = len(ustring1) + 1
    length2 = len(ustring2) + 1
    c = [ [0]*length2  for i in range(length1) ]
    for i in range(1, length1):
        for j in range(1,length2):
            if (ustring1[i-1] == ustring2[j-1]):
                c[i][j] = c[i-1][j-1] + 1
            elif (c[i-1][j] > c[i][j-1]):
                c[i][j] = c[i-1][j]
            else:
                c[i][j] = c[i][j-1]
    ret = c[length1-1][length2-1]
    del c
    return ret



def min_edit_distance(ustring1, ustring2):
    """
    get min edit distance
    """
    if (u""== ustring1 or u"" == ustring2):
        return max(len(ustring1), len(ustring2))
    n = len(ustring1) + 1
    m = len(ustring2) + 1
    distance = [ [0]*m for i in range(n)]
    for i in range(1,n):
        distance[i][0] = distance[i-1][0] + 1
    for j in range(1, m):
        distance[0][j] = distance[0][j-1] + 1
    
    for i in range(1, n):
        for j in range(1, m):
            ins = distance[i-1][j] + 1
            dels = distance[i][j-1] + 1
            add_sub = 2
            if (ustring1[i-1] == ustring2[j-1]):
                add_sub = 0
            sub = distance[i-1][j-1] + add_sub
            distance[i][j] = min((ins, dels, sub))
    ret = distance[n-1][m-1]
    del distance
    return ret



def lcs_dis_pro(ustring1, ustring2):
    """
    lcs_len(x,y) / max(x,y)
    """
    if (u""== ustring1 or u"" == ustring2):
        return 0.0
    ret = lcs_len(ustring1, ustring2)
    max_length = max(len(ustring1), len(ustring2))
    ret_score = 0.0
    if max_length > 0.01:
        ret_score = float(ret) / max_length
    return ret_score



#--------------- the disatrance of vector ----------------
# input  {word1:weight1, word2: weight2}
#---------------------------------------------------------

def euclidean_distance(x_dict, y_dict):
    """
    Euclidean distance
    Returns:
        None: param error
        float: the distance of two vector
    """
    if not isinstance(x_dict, dict) \
        or not isinstance(y_dict, dict):
        return None

    feature = copy.deepcopy(x_dict)
    for key in y_dict:
        if (key in feature):
            feature[key] -= y_dict[key]
        else:
            feature[key] =  y_dict[key]
    tmp_sum = 0.0
    for key in feature:
        tmp_sum += abs(feature[key]) ** 2
    return math.sqrt(tmp_sum)
    

def jffreys_matusita_distance(x_dict, y_dict):
    """
    Jffreys & Matusita distance
    """
    if not isinstance(x_dict, dict) \
        or not isinstance(y_dict, dict):
        return None
    feature = {}
    for key in x_dict:
        feature[key] = math.sqrt(x_dict[key])
    for key in y_dict:
        if (key in feature):
            feature[key] -= math.sqrt(y_dict[key])
        else:
            feature[key] =  math.sqrt(y_dict[key])
    
    tmp_sum = 0.0
    for key in feature:
        tmp_sum += (feature[key]) ** 2
    return math.sqrt(tmp_sum)



def sim_cos(x_dict, y_dict):
    """
    cos(x, y)
    """
    if not isinstance(x_dict, dict) \
        or not isinstance(y_dict, dict):
        return 0.0
    x_dis = 0.0
    y_dis = 0.0
    sum_dis = 0.0
    x_dis = sum([x_dict[key] ** 2  for key in x_dict])
    for key in y_dict:
        y_dis += y_dict[key] ** 2
        if key in x_dict:
            sum_dis += x_dict[key] * y_dict[key]
    denominator =  float(math.sqrt(x_dis) * math.sqrt(y_dis))
    result = 1.0
    if (0 != denominator):
        result = float(sum_dis) / denominator
    return result



def sim_dice(x_dict, y_dict):
    """
    dice(s1, s2) = 2*comm(s1,s2)/(leng(s1)+leng(s2))
    """
    if not (isinstance(x_dict, dict) or isinstance(y_dict, dict)):
        sys.stderr.write("param error: in sim_dice function\n")
        return 0.0
    
    feature = {}
    x_dis = 0.0
    y_dis = 0.0
    sum_dis = 0.0
    for key in x_dict:
        x_dis += x_dict[key] ** 2
        feature[key] = x_dict[key]
    for key in y_dict:
        y_dis += y_dict[key] ** 2
        if (key in feature):
            sum_dis += feature[key] * y_dict[key]
    denominator = float(x_dis * y_dis)
    ret_score = 1.0
    if denominator > 0.001:
        ret_score = float(2 * sum_dis) / denominator
    return ret_score


