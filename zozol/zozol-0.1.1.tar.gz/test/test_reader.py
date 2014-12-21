import os.path
from zozol import decode_ber, base as asn1, markers as m
from zozol.schemas.pkcs7_dstszi import ContentInfo
from gost89 import gosthash

def here(fname):
    dirname, _ = os.path.split(__file__)
    return os.path.join(dirname, fname)

def test_pkcs7():
    CONTENT = """IGNORE THIS FILE.
This file does nothing, contains no useful data, and might go away in
future releases.  Do not depend on this file or its contents.
"""

    data = open(here('signed1.r')).read()
    msg = ContentInfo.stream(bytearray(data), len(data), decode_ber)
    assert str(msg.content.contentInfo.content) == CONTENT
    assert msg.content.signerInfos[0].sid.serialNumber.value == 359272175317388400160838857906663248925214184704
    sign_hex = '909653756d2f0f9702498e0925e2d1a50e8aa617d31680c4459cb441ef8c6b620e86de8e37036ba599c61719729a3b75339216a250839b4ff867e4e13b79630d'
    assert str(msg.content.signerInfos[0].encryptedDigest) == sign_hex.decode('hex')


def test_pkcs7_certtax():
    data = open(here('signed1.r')).read()
    msg = ContentInfo.stream(bytearray(data), len(data), decode_ber)
    x509 = msg.content.certificates[0]
    assert x509.subject_edrpou == '3225813873'
    assert x509.subject_drfo == '3225813873'


def test_implicit():
    class X(asn1.Seq):
        fields = [
            ('b', m.Explicit(tag=0, typ=asn1.OctStr))
        ]

    data = bytearray(str.decode('3007A0050403313233', 'hex'))
    x = X.stream(data, len(data), decode_ber)
    assert str(x.b) == '123'


def test_optional():
    class X(asn1.Seq):
        fields = [
            ('a', m.Optional(asn1.Int)),
            ('b', m.Explicit(tag=0, typ=asn1.OctStr))
        ]

    data = bytearray(str.decode('3007A0050403313233', 'hex'))
    x = X.stream(data, len(data), decode_ber)
    assert str(x.b) == '123'
    assert not hasattr(x, 'a')


def test_optional_last():
    class A(asn1.Seq):
        fields = [
            ('key', asn1.Bool),
            ('opt', m.Optional(asn1.Bool)),
        ]

    data = bytearray(str.decode('30030101ff', 'hex'))
    a = A.stream(data, decode_fn=decode_ber)
    assert a.key.value is True
    assert not hasattr(a, 'opt')


def test_default():
    class A(asn1.Seq):
        fields = [
            ('key', asn1.Bool),
            ('opt', m.Default(value='default', typ=asn1.OctStr)),
        ]

    data = bytearray(str.decode('30030101ff', 'hex'))
    a = A.stream(data, decode_fn=decode_ber)
    assert a.key.value is True
    assert a.opt.value == 'default'


def test_seq_int():
    class B(asn1.Int):
        pass

    data = bytearray(str.decode('0202FF01', 'hex'))
    b = B.stream(data, decode_fn=decode_ber)
    assert b.value == 0xFF01, str(b)


def test_explicit():
    class E(asn1.Seq):
        fields = [
            ('name', m.Explicit(tag=2, typ=asn1.OctStr))
        ]

    data = bytearray(str.decode('3005a203040158', 'hex'))
    e = E.stream(data, decode_fn=decode_ber)
    assert str(e.name) == 'X'


def test_explicit_raw():
    data = bytearray(str.decode('a203040158', 'hex'))
    source = decode_ber(data, len(data))
    tag, cls, content = source.next()
    assert tag == 2

    source = decode_ber(content.data, content.tlen, content.off)
    tag, cls, content = source.next()
    assert tag == 4
    assert cls == 'univ', cls
    assert str(content) == 'X'


def test_bool():
    data = bytearray(str.decode('0101ff', 'hex'))
    b = asn1.Bool.stream(data, decode_fn=decode_ber)
    assert b.value is True


def test_int():
    data = bytearray(str.decode('02020080', 'hex'))
    d = asn1.Int.stream(data, decode_fn=decode_ber)
    assert d.value == 128


def test_hashsum():
    data = open(here('signed1.r')).read()
    msg = ContentInfo.stream(bytearray(data), len(data), decode_ber)
    attrs = msg.content.signerInfos[0].authenticatedAttributes
    dgst = str(attrs['1.2.840.113549.1.9.4'][0].data)
    cdgst = gosthash(str(msg.content.contentInfo.content))

    assert cdgst == dgst

    dgst = str(attrs.messageDigest)
    assert cdgst == dgst
