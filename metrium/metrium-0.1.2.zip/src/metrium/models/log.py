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

import flask

import quorum

from metrium.models import base
from metrium.models import account

class Log(base.Base):

    message = dict(
        index = True
    )

    type = dict(
        index = True
    )

    owner_extra = dict(
        index = True
    )

    owner = dict(
        type = quorum.reference(
            account.Account,
            name = "username"
        )
    )

    @classmethod
    def validate_new(cls):
        return super(Log, cls).validate_new() + [
            quorum.not_null("message"),
            quorum.not_empty("message"),
            quorum.string_gt("message", 4),

            quorum.not_null("type"),
            quorum.not_empty("type"),

            quorum.not_null("owner_extra")
        ]

    @classmethod
    def get_state(cls):
        events = []
        logs = cls.find(sort = [("timestamp", -1)], limit = 10)

        for log in logs:
            event = log.get_event()
            events.append({
                "contents" : event
            })

        return {
            "log.message" : events
        }

    @classmethod
    def notify(cls, message, type = "info", owner_extra = "anonymous"):
        log = cls()
        log.message = message
        log.type = type
        log.owner_extra = owner_extra
        log.save()

    @classmethod
    def _build(cls, model, map):
        base.Base._build(model, map)
        owner_extra = model.get("owner_extra", False)
        owner = model.get("owner", None)
        model["_owner"] = owner_extra or (owner and owner.username)

    def get_event(self):
        return dict(
            message = self.message,
            type = self.type,
            owner = self.get_owner(),
            timestamp = self.timestamp,
            time_s = self.time_s()
        )

    def pre_create(self):
        base.Base.pre_create(self)

        try: username = flask.session.get("username", None)
        except: username = None
        self.owner = username

    def post_create(self):
        base.Base.post_create(self)

        pusher = quorum.get_pusher()
        pusher["global"].trigger("log.message", {
            "contents" : self.get_event()
        })

    def get_owner(self):
        if self.owner_extra: return self.owner_extra
        if self.owner: return self.owner.username
        return None
