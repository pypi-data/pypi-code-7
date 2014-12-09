# -*- coding: utf-8 -*-

"""Class to override field names in models or records.
   Assign an instance of FieldMapping to the _mapping_ attribute of
   a form class to use.
"""

# pylint: disable=W0212,R0903

# W0212: Access to protected members _fields and _metafields.
# R0903: Too few public methods (zero).


import pprint
from dk import modelinfo


class FieldMapping(object):
    "Default dict like class to override field names in forms classes."
    
    def __init__(self, cls, **kw):
        self.cls = cls
        self.kw = {}
        self.default = {}

        if hasattr(self.cls, '_metafields'):
            # orm.Record instance
            for fname in self.cls._fields:
                mf = self.cls._metafields[fname]
                defval = mf.verbose_name.replace(u'_', u' ').title()
                self.default[fname] = defval

        elif hasattr(self.cls, '_meta'):
            # Django model instance
            m = modelinfo.info(self.cls)
            for fname, fi in m.field_info:
                if isinstance(fi.verbose_name, unicode):
                    vname = fi.verbose_name
                elif isinstance(fi.verbose_name, str):
                    vname = fi.verbose_name.decode('u8')
                defval = vname.replace(u'_', u' ').title()
                self.default[fname] = defval

        else:
            self.default.update(kw)

        self.kw.update(self.default)
        self.kw.update(kw)

    def __getitem__(self, key):
        return self.kw.get(key, key)

    def __repr__(self):
        res = u'[%s] {\n %s\n}' % (self.cls.__name__,
                                   pprint.pformat(self.kw)[1:-1])
        return res.encode('l1', 'ignore')
