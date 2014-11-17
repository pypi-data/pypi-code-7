#!/usr/bin/env python

"""
Pandoc filter to allow interpolation of metadata fields
into a document.  %{fields} will be replaced by the field's
value, assuming it is of the type MetaInlines or MetaString.
"""

from pandocfilters import toJSONFilter, attributes, Span, Str
import re

pattern = re.compile('%\{(.*)\}$')


def metavars(key, value, format, meta):
    if key == 'Str':
        m = pattern.match(value)
        if m:
            field = m.group(1)
            result = meta.get(field, {})
            if 'MetaInlines' in result:
                return Span(attributes({'class': 'interpolated',
                                        'field': field}),
                            result['MetaInlines'])
            elif 'MetaString' in result:
                return Str(result['MetaString'])

if __name__ == "__main__":
    toJSONFilter(metavars)
