from __future__ import print_function
import datetime
import types
from . markers import Optional, Default, Implicit, Explicit
from . rewindable import Rewindable
from . util import u


class Impossible(object):
    pass

impossible = Impossible()

class Asn1Tag(object):
    primitive = True

    def __init__(self, data=None, decode_fn=None, value=None, tag=None):
        if data:
            assert not isinstance(data, Asn1Tag)
            self.read(data)
        else:
            self.value = value

    @classmethod
    def from_data(cls, data, decode_fn=None, tag=None, **kwargs):
        if isinstance(data, cls) is cls:
            return data

        if issubclass(cls, type(data)):
            rt = cls(value=data.value)
            return rt

        return cls(data, decode_fn=decode_fn)

    @classmethod
    def to_data(cls, data, parent):
        return data

    @classmethod
    def stream(cls, data, tlen=None, decode_fn=None):
        if type(data) is not Rewindable:
            tlen = tlen or len(data)
            data = Rewindable(decode_fn(data, tlen))

        tag, clsname, content = data.next()
        if tag != cls.tag:
            raise ValueError("Schema mismcatch tag {}".format(tag))

        if type(content) is Rewindable:
            return cls(content, decode_fn)
        return content

    def encode_type(self, el, desc):
        tag = el.tag
        cls = 0
        content = el.encode()
        wrapTag = None
        if type(desc) is Explicit:
            wrapTag = desc.tag |  0x20
            desc = desc.typ

        if type(desc) is Implicit:
            tag = desc.tag
            cls = 2
            desc = desc.typ
            bconstructed = 0 if desc.primitive else 0x20
            tag |= bconstructed

        if type(desc) is types.FunctionType:
            desc = desc(self)

        ret = desc.to_data((tag, cls, content), self)
        if wrapTag is not None:
            ret = (wrapTag, 2, (ret,))

        return ret


class Seq(Asn1Tag):
    tag = 0x10
    primitive = False

    def __init__(self, source=None, decode_fn=None, tag=None, value=None):
        self.elements = []
        if type(source) is Rewindable:
            self.read(source, decode_fn)

        self.source = source

    def read(self, source, decode_fn):
        self.read_fields(source, decode_fn)

    def read_fields(self, source, decode_fn):
        fields = self.fields[:]

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
                    setattr(self, name, desc(value=fallback))
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
                    setattr(self, name, desc(value=fallback))
                    continue
                else:
                    raise ValueError("Input doesnt match schema at {} {} {}".format(name, hex(desc.tag), hex(tag)))

            if type(desc) is Explicit:
                content = decode_fn(content.data, content.tlen, content.off)
                tag, cls, content = next(content)
                desc = desc.typ

            if type(desc) is Implicit:
                desc = desc.typ
                if issubclass(desc, (Seq, SetOf)):
                    content = decode_fn(content.data, content.tlen, content.off)
                else:
                    content = content.data[content.off:content.off+content.tlen]

            if type(desc) is types.FunctionType:
                desc = desc(self)

            content = desc.from_data(content, decode_fn, tag=tag, parent=self)
            setattr(self, name, content)
            self.elements.append(name)

    def to_stream(self, encode_fn):
        return encode_fn(((
            self.tag | 0x20, 0, self.gen_contents()
        ),))

    def encode(self, cls=0):
        return self.gen_contents()

    def gen_contents(self):
        fields = self.fields[:]

        while fields:
            name, desc = fields.pop(0)
            if type(desc) is types.FunctionType:
                desc = desc(self)

            is_optional = False
            is_default = False
            default_value = impossible

            if type(desc) is Optional:
                desc = desc.typ
                is_optional = True

            if type(desc) is Default:
                default_value = desc.value
                desc = desc.typ
                is_default = True

            try:
                el = getattr(self, name)
            except AttributeError:
                if is_optional or is_default:
                    continue
                raise

            if is_default and default_value == el.value:
                continue

            yield self.encode_type(el, desc)

    def __repr__(self):
        return '<Seq {} of {}>'.format(self.__class__.__name__, str.join(', ', self.elements))


class ObjId(Asn1Tag):
    tag = 0x06

    def read(self, data):
        current = data[0]
        numbers = [int(current / 40), current % 40]
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

    def encode(self):
        ret = bytearray()
        numbers = self.value[:]
        n1, n2 = numbers.pop(0), numbers.pop(0)
        ret.append((n1 * 40) + n2)
        while numbers:
            n = numbers.pop(0)
            if n == 0:
                ret.append(n)
                continue

            off = len(ret)
            while n:
                nb = n & 0x7F
                ret.insert(off, nb | 0x80)
                n >>= 7

            ret[-1] &= 0x7F

        return ret


class OctStr(Asn1Tag):
    tag = 0x04

    def read(self, data):
        self.value = u(data, 'latin1')

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, str.encode(str(self.value), 'hex'))

    def __str__(self):
        return str(self.value)

    def encode(self):
        return bytearray(self.value, 'latin1')


class Utf8Str(OctStr):
    tag = 0x0C
    def read(self, data):
        self.value = u(data, 'utf8')

    def encode(self):
        return bytearray(self.value, 'utf-8')

    def __repr__(self):
        return '<{} UTF8 {}>'.format(self.__class__.__name__, self.value.encode('utf8'))


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

    def encode(self):
        if not self.value:
            return bytearray([0])

        ret = bytearray()
        value = self.value
        while value:
            ret.insert(0, value & 0xFF)
            value >>= 8
        return ret


class Bool(Asn1Tag):
    tag = 0x1

    def read(self, data):
        self.value = bool(data[0])

    def encode(self):
        ret = 0xFF if self.value else 00
        return bytearray([ret])


class SetOf(Asn1Tag):
    tag = 0x11
    typ = None
    primitive = False
    def __init__(self, data, decode_fn, tag=None, value=None):
        self.elements = []
        if data and self.typ:
            self.read(data, decode_fn)
        else:
            self.data = data

    def read(self, source, decode_fn):
        for tag, cls, content in source:
            content = self.typ.from_data(content, decode_fn, tag=tag, parent=self)
            self.elements.append(content)

    def __repr__(self):
        return '<SetOf {}: {}>'.format(
            self.typ, 
            str.join(', ', map(repr, self.elements))
        )

    def __getitem__(self, idx):
        return self.elements[idx]

    def to_stream(self, encode_fn):
        return encode_fn(((
            self.tag | 0x20, 0, self.gen_contents()
        ),))

    def encode(self, cls=0):
        return  self.gen_contents()

    def gen_contents(self):
        desc = self.typ
        for el in self.elements:
            yield self.encode_type(el, desc)


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

    def encode(self):
        return bytearray(self.value.strftime('%y%m%d%H%M%SZ'), 'latin1')


class Any(object):
    primitive = True
    def __init__(self, data, decode_fn=None, tag=None, *args, **kwargs):
        if type(data) is Rewindable:
            data = data.data[data.off:data.tlen+data.off]
        self.data = data
        self.tag = tag
        self.primitive = (0x13 & tag) not in [0x10, 0x11]

    @classmethod
    def from_data(cls, data, *args, **kwargs):
        return cls(data, *args, **kwargs)

    @classmethod
    def to_data(cls, data, parent):
        return data

    def encode(self):
        if hasattr(self.data, 'encode'):
            return self.data.encode()
        return self.data
