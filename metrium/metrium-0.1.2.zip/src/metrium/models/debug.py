#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Metrium System
# Copyright (C) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Metrium System.
#
# Hive Metrium System is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Metrium System is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Metrium System. If not, see <http://www.gnu.org/licenses/>.

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

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import datetime

from metrium.models import base

MAXIMUM_MESSAGES = 1000
""" The maximum allowed number of messages, messages after
this offset value will be deleted when the garbage collection
trigger value is enabled """

class Debug(base.Base):

    message = dict()

    lines = dict(
        type = list
    )

    @classmethod
    def log(cls, message, lines = []):
        debug = cls()
        debug.message = message
        debug.lines = lines
        debug.save()

        if not debug.id % MAXIMUM_MESSAGES == 0: return

        outdated = cls.find(skip = MAXIMUM_MESSAGES, sort = [("timestamp", -1)])
        for item in outdated: item.delete()

    @classmethod
    def _build(cls, model, map):
        base.Base._build(model, map)
        timestamp = model.get("timestamp", None)
        timestamp_date = timestamp and datetime.datetime.utcfromtimestamp(timestamp)
        timestamp_string = timestamp_date and timestamp_date.strftime("%d/%m/%Y %H:%M:%S")
        model["timestamp_l"] = timestamp_string
