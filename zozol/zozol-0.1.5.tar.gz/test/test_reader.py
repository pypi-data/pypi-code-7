import os.path
from zozol import decode_ber, base as asn1, markers as m
from zozol.schemas.pkcs7_dstszi import ContentInfo
from zozol.util import u
from gost89 import gosthash

def here(fname):
    dirname, _ = os.path.split(__file__)
    return os.path.join(dirname, fname)

def test_pkcs7():
    CONTENT = """IGNORE THIS FILE.
This file does nothing, contains no useful data, and might go away in
future releases.  Do not depend on this file or its contents.
"""

    data = open(here('signed1.r'), 'rb').read()
    msg = ContentInfo.stream(bytearray(data), len(data), decode_ber)
    assert str(msg.content.contentInfo.content) == CONTENT
    assert msg.content.signerInfos[0].sid.serialNumber.value == 359272175317388400160838857906663248925214184704
    sign = bytearray(b'\x90\x96Sum/\x0f\x97\x02I\x8e\t%\xe2\xd1\xa5\x0e\x8a\xa6\x17\xd3\x16\x80\xc4E\x9c\xb4A\xef\x8ckb\x0e\x86\xde\x8e7\x03k\xa5\x99\xc6\x17\x19r\x9a;u3\x92\x16\xa2P\x83\x9bO\xf8g\xe4\xe1;yc\r')
    assert msg.content.signerInfos[0].encryptedDigest.value == u(sign, 'latin1')


def test_pkcs7_certtax():
    data = open(here('signed1.r'), 'rb').read()
    msg = ContentInfo.stream(bytearray(data), len(data), decode_ber)
    x509 = msg.content.certificates[0]
    assert x509.subject_edrpou == '3225813873'
    assert x509.subject_drfo == '3225813873'


def test_implicit():
    class X(asn1.Seq):
        fields = [
            ('b', m.Explicit(tag=0, typ=asn1.OctStr))
        ]

    data = bytearray(b'\x30\x07\xA0\x05\x04\x03\x31\x32\x33')
    x = X.stream(data, len(data), decode_ber)
    assert str(x.b) == '123'


def test_optional():
    class X(asn1.Seq):
        fields = [
            ('a', m.Optional(asn1.Int)),
            ('b', m.Explicit(tag=0, typ=asn1.OctStr))
        ]

    data = bytearray(b'\x30\x07\xA0\x05\x04\x03\x31\x32\x33')
    x = X.stream(data, len(data), decode_ber)
    assert str(x.b) == '123'
    assert not hasattr(x, 'a')


def test_optional_last():
    class A(asn1.Seq):
        fields = [
            ('key', asn1.Bool),
            ('opt', m.Optional(asn1.Bool)),
        ]

    data = bytearray(b'\x30\x03\x01\x01\xff')
    a = A.stream(data, decode_fn=decode_ber)
    assert a.key.value is True
    assert not hasattr(a, 'opt')


def test_default():
    class A(asn1.Seq):
        fields = [
            ('key', asn1.Bool),
            ('opt', m.Default(value='default', typ=asn1.OctStr)),
        ]

    data = bytearray(b'\x30\x03\x01\x01\xff')
    a = A.stream(data, decode_fn=decode_ber)
    assert a.key.value is True
    assert a.opt.value == 'default'


def test_seq_int():
    class B(asn1.Int):
        pass

    data = bytearray(b'\x02\x02\xFF\x01')
    b = B.stream(data, decode_fn=decode_ber)
    assert b.value == 0xFF01, str(b)


def test_explicit():
    class E(asn1.Seq):
        fields = [
            ('name', m.Explicit(tag=2, typ=asn1.OctStr))
        ]

    data = bytearray(b'\x30\x05\xa2\x03\x04\x01\x58')
    e = E.stream(data, decode_fn=decode_ber)
    assert str(e.name) == 'X'


def test_explicit_raw():
    data = bytearray(b'\xa2\x03\x04\x01\x58')
    source = decode_ber(data, len(data))
    tag, cls, content = next(source)
    assert tag == 2

    source = decode_ber(content.data, content.tlen, content.off)
    tag, cls, content = next(source)
    assert tag == 4
    assert cls == 0, cls
    assert str(content) == 'X'


def test_bool():
    data = bytearray(b'\x01\x01\xff')
    b = asn1.Bool.stream(data, decode_fn=decode_ber)
    assert b.value is True


def test_int():
    data = bytearray(b'\x02\x02\x00\x80')
    d = asn1.Int.stream(data, decode_fn=decode_ber)
    assert d.value == 128


def test_hashsum():
    data = open(here('signed1.r'), 'rb').read()
    msg = ContentInfo.stream(bytearray(data), len(data), decode_ber)
    attrs = msg.content.signerInfos[0].authenticatedAttributes
    dgst = attrs['1.2.840.113549.1.9.4'][0].data.value.encode('latin1')
    cdgst = gosthash(msg.content.contentInfo.content.value.encode('latin1'))

    assert cdgst == dgst

    dgst = attrs.messageDigest.value.encode('latin1')
    assert cdgst == dgst
