# -*- coding: utf-8 -*-
import re
from collections import OrderedDict as kv


__title__ = 'accept'
__version__ = '0.1.0'
__author__ = 'Rhys Elsmore'
__license__ = 'ISC'
__copyright__ = 'Copyright 2015 Rhys Elsmore'
__docformat__ = 'restructuredtext'


class MediaType(object):

    def __init__(self, media_type, q=None, params=None):
        self._media_type = media_type
        self._quality = q or 1.0
        self._params = params or {}

    def __repr__(self):
        return "<Media Type: %s>" % self

    def __str__(self):
        if len(self.params) > 0:
            p = '; '.join(["%s=%s" % (k, v) for k, v in self.params.items()])
            return '%s; q=%s; %s' % (self.media_type, self.q, p)
        else:
            return '%s; q=%s' % (self.media_type, self.q)

    def __getitem__(self, key):
        return self.params.get(key)

    def __eq__(self, other):
        return (self.media_type == other.media_type and
                self.quality == other.quality and self.params == other.params)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return self._compare(other) == -1

    def __gt__(self, other):
        return self._compare(other) > -1

    @property
    def media_type(self):
        return self._media_type

    @property
    def quality(self):
        return self._quality

    @property
    def q(self):
        return self.quality

    @property
    def params(self):
        return self._params

    @property
    def all_types(self):
        return self.media_type == '*/*'

    @property
    def all_subtypes(self):
        return self.media_type.split('/')[1] == '*'

    def _compare(self, other):
        if self.quality > other.quality:
            return -1
        elif self.quality < other.quality:
            return 1
        elif (not self.all_subtypes and other.all_subtypes) or\
                (not self.all_types and other.all_types):
            return -1
        elif (self.all_subtypes and not other.all_subtypes) or\
                (self.all_types and not other.all_types):
            return 1
        elif len(self.params) > len(other.params):
            return -1
        elif len(self.params) == len(other.params):
            return 0
        else:
            return 1


def parse(value):
    results = []
    if not value:
        return results
    value = re.sub(r'^Accept\:\s', '', value)
    for media_range in [m.strip() for m in value.split(',') if m]:
        parts = media_range.split(";")
        media_type = parts.pop(0).strip()
        params = []
        q = 1.0
        for part in parts:
            if not part:
                continue
            (key, value) = part.lstrip().split("=", 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            if key == "q":
                try:
                    q = float(value)
                except:
                    pass
            else:
                params.append((key, value))
        results.append(
            MediaType(media_type, q, kv(params))
        )
    results.sort()
    return results
