# coding=utf-8
from __future__ import unicode_literals
import operator as op


def generate_site_name(name):
    words = name.replace('-', ' ').replace('_', ' ').split()
    return ' '.join(map(unicode.title, words))


def generate_site_brand(name):
    words = name.replace('-', ' ').replace('_', ' ').split()
    return unicode.upper('SYS ' + ''.join(map(op.itemgetter(0), words)))
