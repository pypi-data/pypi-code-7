# -*- coding: utf-8 -*-

"""This module contains enough knowledge about `struct` format strings to
   figure out size and position of fields.
"""
import re
import struct
from struct import Struct
from .utils import split_fields


class Field(object):
    """Representation of a field defined in a `struct` format string.
       (should only be created from :class:`Layout`.
    """

    def __init__(self, **kw):
        # defaults
        self.name = ""
        self.index = 0
        self.position = 0
        self.layout = ""
        self.count = 0
        self.format = 'x'
        self.type = ""
        self.size = 0
        # should padding bytes be stripped when pretty printing
        self.strip = None
        
        self.__dict__.update(kw)
        if self.strip is None:
            self.strip = self.format == 's'

    def get_value(self, data):
        "Get this field's value from `data`."
        rec = struct.unpack_from(
            '=' + self.layout,
            str(data), self.position
        )
        if self.format == 's' and self.strip:
            return rec[0].rstrip('\0')
        return rec[0]

    def set_value(self, data, value):
        "Set this field to `value` in `data`."
        struct.pack_into('=' + self.layout, data, self.position, value)
        return value

    def __repr__(self):
        return '<Field:%s [%d] "%s" count=%d format=%r type="%s" size=%d>' % (
            self.name,
            self.index,
            self.layout,
            self.count,
            self.format,
            self.type,
            self.size
        )

    def __str__(self):
        return "#%-2d %14s %5s = %d" % (self.index, self.name, self.layout, self.size)

    def __len__(self):
        return self.size


class Layout(object):
    """Record layout.

       Usage::

           record_layout = Layout(
                '=12x?3sQ16s16s68s128sHcc',
                'pad',
                'local',
                'rectype',
                'timestamp',
                'salt',
                'digest',
                'key',
                'data',
                'chksum',
                'cr',
                'nl',
                name="Record"
            )


    """
    #: types corresponding to struct character codes
    struct_field_types = {
        'x': "pad byte",
        'c': "char",
        'b': "signed char",
        'B': "unsigned char",
        '?': "_Bool",
        'h': "short",
        'H': "unsigned short",
        'i': "int",
        'I': "unsigned int",
        'l': "long",
        'L': "unsigned long",
        'q': "long long",
        'Q': "unsigned long long",
        'n': "ssize_t",
        'N': "size_t",
        'f': "float",
        'd': "double",
        's': "char[]",
        'p': "char[]",
        'P': "void *",
    }

    #: byte sizes corresponding to struct character codes
    struct_field_sizes = {
        'x': 1,
        'c': 1,
        'b': 1,
        'B': 1,
        '?': 1,
        'h': 2,
        'H': 2,
        'i': 4,
        'I': 4,
        'l': 4,
        'L': 4,
        'q': 8,
        'Q': 8,
        'n': 8,
        'N': 4,
        'f': 4,
        'd': 8,
        's': 1,
        'p': 1,
        'P': 4,
    }

    #: legal struct format string record prefixes
    record_prefix = {
        '@': "native aligned",
        '=': "native",
        '<': "little-endian",
        '>': "big-endian",
        '!': "network-endian",
    }

    #: regex matching one field in a struct format string
    layoutre = re.compile(r'''
        (?P<field>\d*[xcbB?hHiIlLqQnNfdspP])
    ''', re.VERBOSE)


    def __init__(self, layout, *names, **kw):
        self.name = kw.get('name')
        self.names = names
        self.layout = layout
        self.struct = Struct(layout)
        if not layout:
            raise ValueError("illegal layout")
        if layout[0] in self.record_prefix:
            prefix = layout[0]
            layout = layout[1:]
        else:
            prefix = '@'
        fields = []        # get field by position
        self._field = {}   # get field by name
        pos = 0
        for i, field in enumerate(self.layoutre.findall(layout)):
            count = int(field[:-1] or '0', 10)
            fmtch = field[-1]
            f = Field(
                name=names[i] if names else "",
                index=i,
                layout=field,
                count=count,
                format=fmtch,
                type=self.struct_field_types[fmtch],
                size=max(1, count) * self.struct_field_sizes[fmtch],
                position=pos
            )
            pos += len(f)
            fields.append(f)
            if f.name:
                self._field[f.name] = f
        self.prefix = prefix
        self.fields = fields

    def __getitem__(self, key):
        """Get field `key`, where key is either the position of the field
           or its name.
        """
        if isinstance(key, int):
            return self.fields[key]
        else:
            return self._field[key]

    def __contains__(self, fieldname):
        """Is there a field named `fieldname`?
        """
        return fieldname in self._field

    def __len__(self):
        """The length of the record is the sum of all fields.
           
           .. todo: This is obviously not correct for any prefix other than '='
                    since it doesn't take padding into account.
        """
        return sum(f.size for f in self.fields)

    def __repr__(self):
        return '{Layout(%d) "%s" %r}' % (len(self), self.prefix, self.fields)

    def __str__(self):
        # res = self.name + "[%d] (%s):\n" % (self.index, self.layout)
        res = 'Layout for %r: (len=%d)\n' % (self.name, len(self))
        for f in self.fields:
            res += '    @%4d:' % f.position + str(f) + '\n'
        return res

    def split(self, data):
        """Split the byte string `data` into a list of substrings holding the
           data for each field.
        """
        llen = len(self)
        dlen = len(data)
        if dlen != llen:
            msg = "Data (%d) doesn't match layout (%s) length (%d): %r" % (
                dlen, self.layout, llen, data)
            raise ValueError(msg)
        return split_fields(data, [f.size for f in self.fields])
