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

import os
import setuptools

setuptools.setup(
    name = "metrium",
    version = "0.1.2",
    author = "Hive Solutions Lda.",
    author_email = "development@hive.pt",
    description = "Pingu Web Interface",
    license = "GNU General Public License (GPL), Version 3",
    keywords = "metrium dashboard metrics television",
    url = "http://metrium.com",
    zip_safe = False,
    packages = [
        "metrium",
        "metrium.bots",
        "metrium.models",
        "metrium.models.config",
        "metrium.views",
        "metrium.views.api",
        "metrium.views.web"
    ],
    package_dir = {
        "" : os.path.normpath("src")
    },
    package_data = {
        "metrium" : [
            "static/css/*",
            "static/images/*.png",
            "static/images/*.ico",
            "static/images/logos/*.png",
            "static/js/*.js",
            "static/js/*.join",
            "static/js/base/*.js",
            "static/sounds/*",
            "templates/*.tpl",
            "templates/accounts/*.tpl",
            "templates/boards/*.tpl",
            "templates/config/*.tpl",
            "templates/debug/*.tpl",
            "templates/log/*.tpl",
            "templates/partials/*.tpl"
        ]
    },
    install_requires = [
        "flask",
        "quorum",
        "pymongo",
        "redis",
        "omni_api"
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ]
)
