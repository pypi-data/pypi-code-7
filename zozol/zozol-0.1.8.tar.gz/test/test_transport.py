# coding=utf8
from __future__ import print_function
import os.path
from zozol import decode_transport, decode_ber
from zozol.schemas.pkcs7_dstszi import ContentInfo


def here(fname):
    dirname, _ = os.path.split(__file__)
    return os.path.join(dirname, fname)


def test_unwrap():
    data = open(here('signed1'), 'rb').read()
    rdata = open(here('signed1.r'), 'rb').read()
    document = decode_transport(data)
    assert document.body == rdata
    assert document.label == 'UA1_SIGN'


def test_headers():
    data = open(here('signed2'), 'rb').read()
    document = decode_transport(data)
    assert document.label == 'UA1_SIGN'
    assert document.headers['SUBJECT'] == u'Квитанція №1 (не прийнято)'
    assert document.body[0] == 0x30, repr(document.body[:100])


def test_broken_encoding():
    data = open(here('signed3'), 'rb').read()
    document = decode_transport(data)
    assert document.label == 'UA1_SIGN'


def test_enveloped():
    data = open(here('signed4'), 'rb').read()
    document = decode_transport(data)
    assert document.label == 'UA1_SIGN'

    msg = ContentInfo.stream(bytearray(document.body), len(data), decode_ber)
    document = decode_transport(bytearray(msg.content.contentInfo.content.value.encode('latin1')))
    assert document.label == 'UA1_CRYPT'
    assert document.headers.get('CERT_PEM') is not None

    try:
        msg = ContentInfo.stream(bytearray(document.body), len(data), decode_ber)
    except KeyError as e:
        assert str(e) == "'1.2.840.113549.1.7.3'"
    else:
        assert False, "Should raise key error"
