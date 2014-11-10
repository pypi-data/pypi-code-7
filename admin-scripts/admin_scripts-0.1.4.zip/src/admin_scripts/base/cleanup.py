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
import subprocess

USAGE_MESSAGE = "cleanup path [extra_argument_1, extra_argument_2, ...]"
""" The usage message """

SCRIPTS_LIST = [
    "stylesheets.py",
    "encoding.py",
    "join.py",
    "trailing_spaces.py"
]
""" The list of scripts to be executed """

SCRIPTS_CONFIGURATION_MAP = {
    "stylesheets.py" : "development/stylesheets.py",
    "encoding.py" : "development/encoding.py",
    "join.py" : "development/join.py",
    "trailing_spaces.py" : "development/trailing_spaces.py"
}
""" The map associating the script name with the name
of the configuration file, so that during execution
the proper values are passed to each script """

CONFIGURATION_RELATIVE_PATH = "../config/"
""" The relative path to the configuration directory """

PYTHON_COMMAND = "python"
""" The python (execution) command """

CONFIGURATION_FLAG = "-c"
""" The flag name for the configuration control """

NT_PLATFORM_VALUE = "nt"
""" The nt platform value """

CE_PLATFORM_VALUE = "ce"
""" The ce platform value """

DOS_PLATFORM_VALUE = "dos"
""" The dos platform value """

WINDOWS_PLATFORMS_VALUE = (
    NT_PLATFORM_VALUE,
    CE_PLATFORM_VALUE,
    DOS_PLATFORM_VALUE
)
""" The windows platform value, that contains the
series of constant values corresponding to the complete
valid platform values for windows """

def run():
    # retrieves the path to the "current" directory
    directory_path = os.path.dirname(__file__)

    # in case the number of arguments
    # is not sufficient
    if len(sys.argv) < 2:
        # prints a series of message about the correct usage
        # of the command line for this command
        print("Invalid number of arguments")
        print("Usage: " + USAGE_MESSAGE)

        # exits the system in error
        sys.exit(2)

    # retrieves the target path for execution and the
    # extra arguments to be used
    target_path = sys.argv[1]
    extra_arguments = sys.argv[2:]

    # retrieves the current os name and then using it
    # sets the shell value to be used in the process
    shell_value = os.name in WINDOWS_PLATFORMS_VALUE and True or False

    # iterates over all the scripts for execution, passing
    # the proper script values into each script for execution
    for script in SCRIPTS_LIST:
        # retrieves the script configuration file name
        script_configuration_file_name = SCRIPTS_CONFIGURATION_MAP[script]

        # creates both the script and the configuration paths
        script_path = os.path.join(directory_path, script)
        configuration_path = os.path.join(
            directory_path,
            os.path.join(CONFIGURATION_RELATIVE_PATH, script_configuration_file_name)
        )

        # resolves both paths as absolute
        script_path = os.path.abspath(script_path)
        configuration_path = os.path.abspath(configuration_path)

        # creates the arguments list from the various
        # processed arguments
        arguments = [PYTHON_COMMAND]
        arguments.append(script_path)
        arguments.append(target_path)
        arguments.append(CONFIGURATION_FLAG)
        arguments.append(configuration_path)
        arguments.extend(extra_arguments)

        # prints a message and flushes the standard output
        print("------------------------------------------------------------------------")
        print("Executing script file: %s" % script)
        print("------------------------------------------------------------------------")
        sys.stdout.flush()

        # opens a sub-process for script execution (and waits for the end of it)
        process = subprocess.Popen(
            arguments,
            stdin = sys.stdin,
            stdout = sys.stdout,
            stderr = sys.stderr,
            shell = shell_value
        )
        process.wait()
        sys.stdout.flush()

        # print a message and flushes the standard output
        print("------------------------------------------------------------------------")
        print("Finished executing script file: %s" % script)
        print("------------------------------------------------------------------------")
        sys.stdout.flush()

if __name__ == "__main__":
    run()
