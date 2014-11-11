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

from metrium import models

from metrium.bots import base
from metrium.main import quorum

SLEEP_TIME = 20.0
""" The default sleep time to be used by the bots
in case no sleep time is defined in the constructor """

class PendingBot(base.Bot):

    def __init__(self, sleep_time = SLEEP_TIME, *args, **kwargs):
        base.Bot.__init__(self, sleep_time, *args, **kwargs)

    def tick(self):
        pendings = self.get_pendings()
        if not pendings: return

        pusher = quorum.get_pusher()
        pusher["global"].trigger("pending.update", {
            "pendings" : pendings
        })

    def get_pendings(self, count = 10):
        config = models.PendingConfig.get()
        folders = config.folders
        items_f = config.items_f()
        signature = config.get_signature()

        outdated = models.Pending.find(folder = {"$nin" : folders})
        for pending in outdated: pending.delete()

        priority = 1

        for folder, severity in items_f:
            conversations = models.Conversation.find(sort = [("date", -1)], folder = folder)

            for conversation in conversations:
                if not conversation.subject: continue

                date = datetime.datetime.utcfromtimestamp(conversation.date)
                date_s = date.strftime("%d/%m")
                sender = conversation.sender_extra or conversation.sender

                pending = models.Pending.get(
                    conversation = conversation.id,
                    raise_e = False
                )

                if pending:
                    pending_changed = not pending.priority == priority or\
                        not pending.severity == severity
                    pending.priority = priority
                    pending.severity = severity
                    pending_changed and pending.save()
                else:
                    pending = models.Pending()
                    pending.priority = priority
                    pending.severity = severity
                    pending.pre = date_s
                    pending.description = conversation.subject
                    pending.author = sender
                    pending.folder = folder
                    pending.conversation = conversation.id
                    pending.save()

                priority += 1

        new_signature = models.Pending.get_signature(count = count)
        has_changed = not signature == new_signature

        if has_changed:
            pendings = models.Pending.get_events(count = count) or []
            config.signature = new_signature
            config.save()
        else: pendings = []

        return pendings
