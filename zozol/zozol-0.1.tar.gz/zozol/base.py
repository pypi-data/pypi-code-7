import datetime
import types
from . markers import Optional, Default, Implicit, Explicit
from . rewindable import Rewindable


class Asn1Tag(object):

    def __init__(self, data=None, decode_fn=None):
        if data:
            self.read(data)

    @classmethod
    def from_data(cls, data, decode_fn=None, *args):
        if type(data) is cls:
            return data

        if isinstance(data, cls):
            rt = cls()
            rt.value = data.value
            return rt

        return cls(data, decode_fn=decode_fn)

    @classmethod
    def stream(cls, data, tlen=None, decode_fn=None):
        if type(data) is not types.GeneratorType:
            tlen = tlen or len(data)
            data = decode_fn(data, tlen)

        tag, clsname, content = data.next()
        if tag != cls.tag:
            raise ValueError("Schema mismcatch tag {}".format(tag))

        if type(content) is types.GeneratorType:
            return cls(content, decode_fn)
        return content


class Seq(Asn1Tag):
    tag = 0x10

    def __init__(self, source=None, decode_fn=None):
        self.elements = []
        if type(source) is types.GeneratorType:
            self.read(source, decode_fn)

        self.source = source

    def read(self, source, decode_fn):
        self.read_fields(source, decode_fn)


    def read_fields(self, source, decode_fn):
        fields = self.fields[:]

        source = Rewindable(source)

        while fields:
            is_optional = False
            is_default = False
            fallback = None
            name, desc = fields.pop(0)
            if type(desc) is types.FunctionType:
                desc = desc(self)

            if type(desc) is Optional:
                desc = desc.typ
                is_optional = True

            if type(desc) is Default:
                is_default = True
                fallback = desc.value
                desc = desc.typ

            try:
                tag, cls, content = source.next()
            except StopIteration:
                if is_default:
                    setattr(self, name, desc(fallback))
                    break

                if is_optional:
                    break

                raise ValueError("Incomplete structure")

            if desc is not Any and desc.tag != tag:
                if is_optional:
                    source.rewind((tag, cls, content))
                    continue
                elif is_default:
                    source.rewind((tag, cls, content))
                    setattr(self, name, fallback)
                    continue
                else:
                    raise ValueError("Input doesnt match schema at {} {} {}".format(name, hex(desc.tag), hex(tag)))

            if type(desc) is Explicit:
                content = decode_fn(content.data, content.tlen, content.off)
                tag, cls, content = content.next()
                desc = desc.typ

            if type(desc) is Implicit:
                desc = desc.typ
                if issubclass(desc, (Seq, SetOf)):
                    content = decode_fn(content.data, content.tlen, content.off)
                else:
                    content = content.data[content.off:content.off+content.tlen]

            if type(desc) is types.FunctionType:
                desc = desc(self)

            content = desc.from_data(content, decode_fn, self)
            setattr(self, name, content)
            self.elements.append(name)

    def __repr__(self):
        return '<Seq {} of {}>'.format(self.__class__.__name__, str.join(', ', self.elements))


class ObjId(Asn1Tag):
    tag = 0x06

    def read(self, data):
        current = data[0]
        numbers = [current / 40, current % 40]
        current = 0
        for n in data[1:]:
            current <<= 7
            current |= n & 0x7F

            if n & 0x80 == 0:
                numbers.append(current)
                current = 0

        self.value = numbers

    def __repr__(self):
        return '<ObjId {}>'.format(str(self))

    def __str__(self):
        return str.join('.', map(str,self.value))


class OctStr(Asn1Tag):
    tag = 0x04

    def read(self, data):
        self.value = data

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, str.encode(str(self.value), 'hex'))

    def __str__(self):
        return str(self.value)


class Utf8Str(OctStr):
    tag = 0x0C
    def read(self, data):
        self.value = unicode(str(data), 'utf8')


class PrintStr(OctStr):
    tag = 0x13

class BitStr(OctStr):
    tag = 0x03


class Int(Asn1Tag):
    tag = 0x02

    def read(self, data):
        value = 0
        off = 0
        ln = len(data)
        while off < ln:
            value <<= 8
            value |= data[off]
            off += 1

        self.value = value

    def __repr__(self):
        return '<Int {}>'.format(self.value)


class Bool(Asn1Tag):
    tag = 0x1

    def read(self, data):
        self.value = bool(data[0])


class SetOf(Asn1Tag):
    tag = 0x11
    typ = None
    def __init__(self, data, decode_fn):
        self.elements = []
        if data and self.typ:
            self.read(data, decode_fn)
        else:
            self.data = data

    def read(self, source, decode_fn):
        for tag, cls, content in source:
            if isinstance(content, (types.GeneratorType, SetOf)):
                content = self.typ(content, decode_fn)
            else:
                content = self.typ(content)
            self.elements.append(content)

    def __repr__(self):
        return '<SetOf {}: {}>'.format(
            self.typ, 
            str.join(', ', map(repr, self.elements))
        )

    def __getitem__(self, idx):
        return self.elements[idx]


class SeqOf(SetOf, Seq):
    tag = 0x10


class Time(Asn1Tag):
    tag = 0x17

    def read(self, data):
        year = int(data[:2] or "0")
        mon = int(data[2:4] or "0")
        day = int(data[4:6] or "0")
        hour = int(data[6:8] or "0")
        nmin = int(data[8:10] or "0")
        nsec = int(data[10:12] or "0")
        
        if year < 70:
            year = 2000 + year
        else:
            year = 1900 + year

        self.value = datetime.datetime(year=year, month=mon, day=day,
                                       hour=hour, minute=nmin,
                                       second=nsec)

    def __repr__(self):
        return '<UTCTime {}>'.format(self.value)


class Any(object):
    def __init__(self, data, *args):
        self.data = data

    @classmethod
    def from_data(cls, data, *args):
        return cls(data)
