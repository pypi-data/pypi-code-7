from .. import base as asn1
from .. markers import Implicit, Explicit, Optional, Default


class AttributeTypeAndValue(asn1.Seq):
    fields = [
        ('type', asn1.ObjId),
        ('value', asn1.Any),
    ]

class RelativeDistinguishedName(asn1.SetOf):
    typ = AttributeTypeAndValue

class RDNSequence(asn1.SeqOf):
    typ = RelativeDistinguishedName

class Name(RDNSequence):
    pass


class DigestAlgorithmIdentifier(asn1.Seq):
    fields = [
        ('algorithm', asn1.ObjId),
        ('parameters', Optional(asn1.Any)),
    ]


class UniqueIdentifier(asn1.BitStr):
    pass


class SubjectPublicKeyInfo(asn1.Seq):
    fields = [
        ('algorithm', DigestAlgorithmIdentifier),
        ('subjectPublicKey', asn1.BitStr),
        
    ]


class Validity(asn1.Seq):
    fields = [
        ('notBefore', asn1.Time),
        ('notAfter', asn1.Time),
    ]


class Strings(asn1.SetOf):
    typ = asn1.PrintStr


class TaxId(asn1.Seq):
    fields = [
        ('attribute', asn1.ObjId),
        ('value', Strings),
    ]

class TaxIds(asn1.SeqOf):
    typ = TaxId

    @property
    def value(self):
        ret = []
        for el in self.elements:
            ret.append((str(el.attribute), el.value[0]))
        return dict(ret)


class ExtnValue(asn1.OctStr):
    TYPES = {
        "2.5.29.14": asn1.OctStr,
        "2.5.29.15": asn1.BitStr,
        "2.5.29.9": TaxIds,
    }

    @classmethod
    def from_data(cls, data, decode_fn, parent, **kwargs):
        desc = cls.TYPES.get(str(parent.extnID))
        if desc is None:
            return asn1.OctStr.from_data(data, decode_fn)

        data = bytearray(data.value, 'latin1')
        return desc.stream(data, decode_fn=decode_fn)

    @classmethod
    def to_data(cls, data, parent):
        desc = cls.TYPES.get(str(parent.extnID))
        if desc is None:
            return data

        return (cls.tag, 0, (data,))


class Extension(asn1.Seq):
    fields = [
        ('extnID', asn1.ObjId),
        ('critical', Default(value=False, typ=asn1.Bool)),
        ('extnValue', ExtnValue),
    ]


class Extensions(asn1.SeqOf):
    typ = Extension

    @property
    def ext(self):
        try:
            return self._ext
        except AttributeError:
            self._ext = self.ext_cache()

        return self._ext

    def ext_cache(self):
        ret = {}
        for ext in self.elements:
            ret[str(ext.extnID)] = ext.extnValue.value

        return ret

    def __getitem__(self, idx):
        return self.ext[idx]

    def __repr__(self):
        return '<Extensions {}>'.format(self.ext.keys())

class TBSCertificate(asn1.Seq):
    fields = [
        ('version', Explicit(tag=0, typ=asn1.Int)),
        ('serialNumber', asn1.Int),
        ('signature', DigestAlgorithmIdentifier),
        ('issuer', Name),
        ('validity', Validity),
        ('subject', Name),
        ('subjectPublicKeyInfo', SubjectPublicKeyInfo),
        ('issuerUniqueID', Optional(Implicit(tag=1, typ=UniqueIdentifier))),
        ('subjectUniqueID', Optional(Implicit(tag=2, typ=UniqueIdentifier))),
        ('extensions', Optional(Explicit(tag=3, typ=Extensions))),
    ]


class Certificate(asn1.Seq):
    fields = [
        ('tbsCertificate', TBSCertificate),
        ('signatureAlgorithm', DigestAlgorithmIdentifier),
        ('signature', asn1.BitStr),
    ]

    @property
    def extensions(self):
        return self.tbsCertificate.extensions

    @property
    def subject_edrpou(self):
        tax = self.extensions['2.5.29.9']
        return str(tax['1.2.804.2.1.1.1.11.1.4.2.1'])

    @property
    def subject_drfo(self):
        tax = self.extensions['2.5.29.9']
        return str(tax['1.2.804.2.1.1.1.11.1.4.1.1'])
