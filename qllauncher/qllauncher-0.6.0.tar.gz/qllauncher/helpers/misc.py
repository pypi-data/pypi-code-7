"""
QuakeLive Launcher
Copyright (C) 2014  Victor Polevoy <vityatheboss@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Victor Polevoy'

import socket


def dict_get_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key


def dict_get_key_index_by_value(dictionary, value):
    i = 0
    for key, val in dictionary.items():
        if val == value:
            return i

        i += 1


def is_connected_to_network():
    remote_server = "www.google.com"

    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(remote_server)
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False

try:
    from shlex import quote as cmd_quote
except ImportError:
    from pipes import quote as cmd_quote
