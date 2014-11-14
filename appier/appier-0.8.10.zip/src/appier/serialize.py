#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import csv
import uuid

from . import model
from . import legacy
from . import typesf
from . import exceptions

def serialize(obj):
    if isinstance(obj, model.Model): return obj.model
    if isinstance(obj, typesf.Type): return obj.json_v()
    if type(obj) == type(None): return ""
    return legacy.UNICODE(obj)

def serialize_csv(items, encoding = "utf-8", strict = False):
    # verifies if the strict mode is active and there're no items defined
    # if that's the case an operational error is raised, otherwise an in
    # case the items are not provided the default (empty string) is returned
    if strict and not items: raise exceptions.OperationalError(
        message = "Empty items object provided, no keys available"
    )
    if not items: return str()

    # builds the encoder taking into account the provided encoding string
    # value, this encoder will be used to encode each of the partial values
    # that is going to be set in the target csv buffer
    encoder = build_encoder(encoding)

    # retrieves the various keys from the first element of the provided sequence
    # of items then runs the eager operation (list loading) and sorts the provided
    # keys according to the default sorting order defined for the sequence
    keys = items[0].keys()
    keys = legacy.eager(keys)
    keys.sort()

    # constructs the first row (names/keys row) using the gathered sequence of keys
    # and encoding them using the currently build encoder
    keys_row = [encoder(key) if type(key) == legacy.UNICODE else\
        key for key in keys]

    # creates the new string buffer and uses it as the basis for the construction of
    # the csv writer object, writing then the already build first row
    buffer = legacy.StringIO()
    writer = csv.writer(buffer, delimiter = ";")
    writer.writerow(keys_row)

    # iterates over the complete set of items to serializa each of it's attribute values
    # using the order defined in the keys sequence that has been defined
    for item in items:
        row = []
        for key in keys:
            value = item[key]
            value = serialize(value)
            is_unicode = type(value) == legacy.UNICODE
            if is_unicode: value = encoder(value)
            row.append(value)
        writer.writerow(row)

    # retrieves the buffer string value as the resulting value and returns it to the
    # caller method as the final result for the csv serialization
    result = buffer.getvalue()
    return result

def serialize_ics(items, encoding = "utf-8"):
    encoder = build_encoder(encoding)

    buffer = legacy.StringIO()
    buffer.write("BEGIN:VCALENDAR\r\n")
    buffer.write("METHOD:PUBLISH\r\n")
    buffer.write("X-WR-TIMEZONE:America/Los_Angeles\r\n")
    buffer.write("CALSCALE:GREGORIAN\r\n")
    buffer.write("VERSION:2.0\r\n")
    buffer.write("PRODID:-//PUC Calendar// v2.0//EN)\r\n")

    for item in items:
        start = item["start"]
        end = item["end"]
        description = item["description"]
        location = item["location"]
        timezone = item.get("timezone", "Etc/GMT")
        _uuid = item.get("uuid", None)
        _uuid = _uuid or str(uuid.uuid4())

        start = encoder(start)
        end = encoder(end)
        description = encoder(description)
        location = encoder(location)
        timezone = encoder(timezone)
        _uuid = encoder(_uuid)

        buffer.write("BEGIN:VEVENT\r\n")
        buffer.write("UID:%s\r\n" % _uuid)
        buffer.write("TZID:%s\r\n" % timezone)
        buffer.write("DTSTART:%s\r\n" % start)
        buffer.write("DTEND:%s\r\n" % end)
        buffer.write("DTSTAMP:%s\r\n" % start)
        buffer.write("SUMMARY:%s\r\n" % description)
        buffer.write("LOCATION:%s\r\n" % location)
        buffer.write("END:VEVENT\r\n")

    buffer.write("END:VCALENDAR\r\n")

    result = buffer.getvalue()
    return result

def build_encoder(encoding):
    if legacy.PYTHON_3: return lambda v: v
    else: return lambda v: v if v == None else v.encode(encoding)
