import os.path
from zozol import decode_ber, encode_ber, encode_ber_tag, base as asn1, markers as m
from zozol.schemas.pkcs7_dstszi import ContentInfo

def here(fname):
    dirname, _ = os.path.split(__file__)
    return os.path.join(dirname, fname)

def test_encode_ocsttr():
    data = encode_ber_tag(0x04, 0, bytearray('123', 'latin1'), bytearray())
    assert data == b'\x04\x03\x31\x32\x33'


def test_encode_ocsttr_long():
    expected = bytearray(b'\x04\x81\x8033333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333')
    data = encode_ber_tag(0x04, 0, bytearray('3' * 128, 'latin1'), bytearray())
    assert data == expected, (repr(data), repr(expected))


def test_encode_ocsttr_long2():
    expected = bytearray(b'\x04\x82\x01\x0133333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333')
    data = encode_ber_tag(0x04, 0, bytearray('3' * 257, 'latin1'), bytearray())
    assert data == expected, (repr(data), repr(expected))


def test_encode_seq():
    seq = (
        (0x30, 0, (
            (0x04, 0, bytearray('123', 'latin1')),
            (0, 2, bytearray('999', 'latin1')),
        ))
    )
    data = encode_ber((seq,))
    assert len(data) == 2 + 2 + 2 + 3 + 3
    assert data[0] == 0x30
    assert data[1] == 2 + 2 + 3 + 3
    assert data[2] == 0x04
    assert data[3] == 3
    assert data[4:7] == bytearray('123', 'latin1')
    assert data[7] == 0x80
    assert data[8] == 3
    assert data[9:12] == bytearray('999', 'latin1')


def test_encode_schema():
    class X(asn1.Seq):
        fields = [
            ('b', asn1.OctStr),
            ('c', asn1.Int),
        ]

    x = X()
    x.b = asn1.OctStr(value='123')
    x.c = asn1.Int(value=2227)

    data = x.to_stream(encode_fn=encode_ber)
    assert bytes(data) == b'\x30\x09\x04\x03\x31\x32\x33\x02\x02\x08\xb3'


def test_encode_implicit():
    class X(asn1.Seq):
        fields = [
            ('b', m.Implicit(tag=0, typ=asn1.OctStr)),
            ('c', asn1.Int),
        ]

    x = X()
    x.b = asn1.OctStr(value='123')
    x.c = asn1.Int(value=2227)

    data = x.to_stream(encode_fn=encode_ber)
    assert bytes(data) == b'\x30\x09\x80\x03\x31\x32\x33\x02\x02\x08\xb3'


def test_encode_explicit():
    class X(asn1.Seq):
        fields = [
            ('b', m.Explicit(tag=0, typ=asn1.OctStr)),
            ('c', asn1.Int),
        ]

    x = X()
    x.b = asn1.OctStr(value='123')
    x.c = asn1.Int(value=2227)

    data = x.to_stream(encode_fn=encode_ber)
    assert bytes(data) == b'\x30\x0B\xA0\x05\x04\x03\x31\x32\x33\x02\x02\x08\xB3'


def test_encode_default():
    class X(asn1.Seq):
        fields = [
            ('c', m.Default(value=2, typ=asn1.Int)),
        ]

    x = X()

    data = x.to_stream(encode_fn=encode_ber)
    assert bytes(data) == b'\x30\x00'

    x.c = asn1.Int(value=2)

    data = x.to_stream(encode_fn=encode_ber)
    assert bytes(data) == b'\x30\x00'

    x.c = asn1.Int(value=3)

    data = x.to_stream(encode_fn=encode_ber)
    assert bytes(data) == b'\x30\x03\x02\x01\x03'


def test_encode_attrs():
    data = open(here('signed1.r'), 'rb').read()
    cattr_data = bytearray(open(here('signed1.attrs'), 'rb').read())

    msg = ContentInfo.stream(bytearray(data), len(data), decode_ber)
    attrs = msg.content.signerInfos[0].authenticatedAttributes
    attr_data = attrs.to_stream(encode_fn=encode_ber)
    cattr_data[0] = 0x31
    assert attr_data == cattr_data


def test_encode_x509():
    data = open(here('signed1.r'), 'rb').read()
    cx509_data = bytearray(open(here('signed1.x509'), 'rb').read())

    msg = ContentInfo.stream(bytearray(data), decode_fn=decode_ber)
    x509 = msg.content.certificates[0]
    x509_data = x509.to_stream(encode_fn=encode_ber)
    assert x509_data == cx509_data


def test_detach():
    data = open(here('signed1.r'), 'rb').read()
    msg = ContentInfo.stream(bytearray(data), decode_fn=decode_ber)
    recode = msg.to_stream(encode_fn=encode_ber)
    assert data == bytes(recode)

    del msg.content.contentInfo.content
    detached_sign_data = msg.to_stream(encode_fn=encode_ber)
    assert detached_sign_data[55] == 0xA0, repr(detached_sign_data[55:60])
    msg = ContentInfo.stream(detached_sign_data, decode_fn=decode_ber)
    assert not hasattr(msg.content.contentInfo, 'content')


def test_choice():
    class IS(m.Choice):
        types = [
            asn1.Int,
            asn1.OctStr,
        ]

    class A(asn1.Seq):
        fields = [
            ('value', IS),
        ]

    a = A()
    a.value = asn1.Int(value=255)
    data = a.to_stream(encode_fn=encode_ber)
    expect_data = bytearray(b'\x30\x03\x02\x01\xff')
    assert data == expect_data

    a = A.stream(data, decode_fn=decode_ber)
    a.value = asn1.OctStr(value='\x0d')
    data = a.to_stream(encode_fn=encode_ber)
    expect_data = bytearray(b'\x30\x03\x04\x01\x0d')
    assert data == expect_data
