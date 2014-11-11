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

import quorum

from metrium.models.config import base

class OmniConfig(base.Config):

    base_url = dict(
        index = True
    )

    username = dict(
        index = True
    )

    password = dict(
        index = True
    )

    registered = dict()

    @classmethod
    def validate_new(cls):
        return super(OmniConfig, cls).validate_new() + [
            quorum.not_null("base_url"),
            quorum.not_empty("base_url"),

            quorum.not_null("username"),
            quorum.not_empty("username"),

            quorum.not_null("password"),
            quorum.not_empty("password"),
        ]

    def pre_create(self):
        base.Config.pre_create(self)

        self.name = "omni"

    def is_registered(self, api, callback_url):
        # verifies that the registered field exists in case
        # it does not returns immediately false (no registration)
        if not hasattr(self, "registered"): return False
        if not self.registered: return False

        # retrieves the base url of the omni api from the api client
        # and then retrieves the (already) registered base url and
        # callback url values and compares them against the new ones
        # that are going to be used in case they are the same the
        # registration is considered to be the same
        base_url = api.base_url
        _base_url, _callback_url = self.registered.split("$", 1)
        return base_url == _base_url and callback_url == _callback_url
