import os.path
from zozol import decode_ber, encode_ber, encode_ber_tag, base as asn1, markers as m
from zozol.schemas.pkcs7_dstszi import ContentInfo

def here(fname):
    dirname, _ = os.path.split(__file__)
    return os.path.join(dirname, fname)

def test_encode_ocsttr():
    data = encode_ber_tag(0x04, 0, bytearray('123'), bytearray())
    assert data == '0403313233'.decode('hex')


def test_encode_ocsttr_long():
    expect_hex = '0481803333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333'
    data = encode_ber_tag(0x04, 0, bytearray('3' * 128), bytearray())
    assert data == expect_hex.decode('hex')


def test_encode_ocsttr_long2():
    expect_hex = '048201013333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333'
    data = encode_ber_tag(0x04, 0, bytearray('3' * 257), bytearray())
    assert data == expect_hex.decode('hex')


def test_encode_seq():
    seq = (
        (0x30, 0, (
            (0x04, 0, '123'),
            (0, 2, '999'),
        ))
    )
    data = encode_ber((seq,))
    assert len(data) == 2 + 2 + 2 + 3 + 3
    assert data[0] == 0x30
    assert data[1] == 2 + 2 + 3 + 3
    assert data[2] == 0x04
    assert data[3] == 3
    assert str(data[4:7]) == '123'
    assert data[7] == 0x80
    assert data[8] == 3
    assert str(data[9:12]) == '999'


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
    assert str(data) == str.decode('30090403313233020208b3', 'hex')


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
    assert str(data) == str.decode('30098003313233020208b3', 'hex')


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
    assert str(data) == str.decode('300BA0050403313233020208B3', 'hex')


def test_encode_default():
    class X(asn1.Seq):
        fields = [
            ('c', m.Default(value=2, typ=asn1.Int)),
        ]

    x = X()

    data = x.to_stream(encode_fn=encode_ber)
    assert str(data) == str.decode('3000', 'hex')

    x.c = asn1.Int(value=2)

    data = x.to_stream(encode_fn=encode_ber)
    assert str(data) == str.decode('3000', 'hex')

    x.c = asn1.Int(value=3)

    data = x.to_stream(encode_fn=encode_ber)
    assert str(data) == str.decode('3003020103', 'hex')


def test_encode_attrs():
    data = open(here('signed1.r')).read()
    cattr_data = bytearray(open(here('signed1.attrs')).read())

    msg = ContentInfo.stream(bytearray(data), len(data), decode_ber)
    attrs = msg.content.signerInfos[0].authenticatedAttributes
    attr_data = attrs.to_stream(encode_fn=encode_ber)
    cattr_data[0] = 0x31
    assert attr_data == cattr_data


def test_encode_x509():
    data = open(here('signed1.r')).read()
    cx509_data = bytearray(open(here('signed1.x509')).read())

    msg = ContentInfo.stream(bytearray(data), decode_fn=decode_ber)
    x509 = msg.content.certificates[0]
    x509_data = x509.to_stream(encode_fn=encode_ber)
    assert x509_data == cx509_data
