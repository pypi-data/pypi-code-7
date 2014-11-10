#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Administration Scripts
# Copyright (c) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Administration Scripts.
#
# Hive Administration Scripts is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Administration Scripts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Administration Scripts. If not, see <http://www.gnu.org/licenses/>.

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
import sys

def configuration(file_path = None, **kwargs):
    """
    Retrieves the configuration map(s) for the given arguments,
    the keyword based arguments are used as the configuration
    in case no valid configuration file exits (fallback).

    @type file_path: String
    @param file_path: The path to the file that is going to be
    processed as the configuration file in context.
    @rtype: Dictionary
    @return: The configuration structure/map, taking into account
    the current location structure.
    """

    # in case the configuration file path is defined, meaning that
    # a configuration file is expected to be loaded
    if file_path:
        # retrieves the configuration directory from the configuration
        # file path (the directory is going to be used to include the module)
        directory_path = os.path.dirname(file_path)
        directory_path = os.path.abspath(directory_path)

        # in case the (configuration directory) path is valid inserts it into the
        # system path, so that it's possible to load python files from it
        directory_path and sys.path.insert(0, directory_path)

        # retrieves the configuration file base path from the configuration file path
        file_base_path = os.path.basename(file_path)

        # retrieves the configuration module name and the configuration module extension
        # by splitting the configuration base path into base name and extension
        module_name, _module_extension = os.path.splitext(file_base_path)

        # imports the configuration module and retrieves the configurations
        # variable containing the "final" configuration structure
        configuration = __import__(module_name)
        configurations = configuration.configurations

    # otherwise the provided arguments (through keyword) are going to be used
    # as the basis for the creation of the configurations
    else:
        # creates the configurations tuple with the base configurations
        # coming from the keyword based arguments (as expected)
        configurations = (kwargs)

    return configurations
