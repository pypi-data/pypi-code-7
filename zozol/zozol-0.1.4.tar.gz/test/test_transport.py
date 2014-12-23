# coding=utf8
from __future__ import print_function
import os.path
from zozol import decode_transport


def here(fname):
    dirname, _ = os.path.split(__file__)
    return os.path.join(dirname, fname)


def test_unwrap():
    data = open(here('signed1')).read()
    rdata = open(here('signed1.r')).read()
    document = decode_transport(data)
    assert document.body == rdata
    assert document.label == 'UA1_SIGN'


def test_headers():
    data = open(here('signed2')).read()
    document = decode_transport(data)
    assert document.label == 'UA1_SIGN'
    assert document.headers['SUBJECT'] == u'Квитанція №1 (не прийнято)'
    assert document.body[0] == 0x30, repr(document.body[:100])
