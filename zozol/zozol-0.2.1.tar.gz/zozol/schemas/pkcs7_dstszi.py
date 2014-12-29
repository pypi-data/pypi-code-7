from .. import base as asn1
from .. markers import Implicit, Explicit, Optional, Choice
from . rfc3280_x509 import Certificate, DigestAlgorithmIdentifier, Name


class ContentInfo(asn1.Seq):
    def resolve_content(obj):
        return TYPES[str(obj.contentType)]

    fields = [
        ('contentType', asn1.ObjId),
        ('content', Optional(Explicit(tag=0, typ=resolve_content))),
    ]


class DigestAlgorithmIdentifiers(asn1.SetOf):
    typ = DigestAlgorithmIdentifier


class ExtendedCertificatesAndCertificates(asn1.SeqOf):
    typ = Certificate


class IssuerAndSerialNumber(asn1.Seq):
    fields = [
        ('issuer', Name),
        ('serialNumber', asn1.Int),
    ]



class SignerIdentifier(Choice):
    types = [
        IssuerAndSerialNumber,
        asn1.OctStr
    ]


class AttributeValues(asn1.SetOf):
    typ = asn1.Any


class Attribute(asn1.Seq):
    fields = [
        ('type', asn1.ObjId),
        ('values', AttributeValues),
    ]

class Attributes(asn1.SetOf):
    typ = Attribute
    HUMAN_NAME = {
        "contentType": "1.2.840.113549.1.9.3",
        "messageDigest": "1.2.840.113549.1.9.4",
        "signingTime ": "1.2.840.113549.1.9.5",
    }

    def _build_attr_cache(self):
        return {
            str(el.type): el.values
            for el in self.elements
        }


    def __getitem__(self, idx):
        try:
            kv = self._attr_cache
        except AttributeError:
            kv = self._build_attr_cache()
            self._attr_cache = kv

        return kv[idx]

    def __getattr__(self, idx):
        objid = self.HUMAN_NAME.get(idx)
        if objid is None:
            raise AttributeError("No attr {} defined".format(idx))

        try:
            return self[objid][0].data
        except KeyError:
            raise AttributeError("Attribute {} not present".format(objid))

class SignerInfo(asn1.Seq):
    fields = [
        ('version', asn1.Int),
        ('sid', SignerIdentifier),
        ('digestAlgorithm', DigestAlgorithmIdentifier),
        ('authenticatedAttributes', Optional(Implicit(tag=0, typ=Attributes))),
        ('digestEncryptionAlgorithm', DigestAlgorithmIdentifier),
        ('encryptedDigest', asn1.OctStr),
        ('unauthenticatedAttributes', Optional(Implicit(tag=1, typ=Attributes))),
    ]


class SignerInfos(asn1.SetOf):
    typ = SignerInfo


class SignedData(asn1.Seq):
    fields = [
        ('version', asn1.Int),
        ('digestAlgorithms', DigestAlgorithmIdentifiers),
        ('contentInfo', ContentInfo),
        ('certificates', Optional(Implicit(tag=0, typ=ExtendedCertificatesAndCertificates))),
        ('crls', Optional(Implicit(tag=1, typ=asn1.Any))),
        ('signerInfos', SignerInfos),

    ]

class Data(asn1.OctStr):
    pass

TYPES = {
    "1.2.840.113549.1.7.2": SignedData,
    "1.2.840.113549.1.7.1": Data,
}

