#!/usr/bin/env python
# -*- coding: utf-8 -*-

# noipy.noipy
# Copyright (c) 2013 Pablo O Vieira (povieira)
# See README.rst and LICENSE for details.

from __future__ import print_function

try:
    import urllib.request as urllib
except ImportError:
    import urllib

import argparse
import sys
import os
import re
import getpass

from . import dnsupdater
from . import authinfo

from . import __version__, __license__

try:
    input = raw_input
except NameError:
    pass


EXECUTION_RESULT_OK = 0
EXECUTION_RESULT_NOK = 1

DEFAULT_CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.noipy')


def get_ip():
    """Return the machine external IP.
    """

    page = urllib.urlopen('http://checkip.dyndns.org')
    content = page.read().decode('utf-8')

    return re.search(r'(\d{1,3}\.?){4}', content).group()


def print_version():
    print("== noipy DDNS updater tool v%s ==" % __version__)


def execute_update(args):
    """Execute the update based on command line args and returns a tuple
    with Exit Code and the processing Status Massage

    @param args:
    @return:
    """

    UpdaterProvider = getattr(dnsupdater,
                              dnsupdater.AVAILABLE_PLUGINS.get(args.provider))

    process_message = None

    auth = None
    if args.store:  # --store argument
        if args.usertoken:
            if args.password:
                auth = authinfo.ApiAuth(args.usertoken, args.password)
            else:
                auth = authinfo.ApiAuth(args.usertoken)
        else:
            if UpdaterProvider.auth_type == 'P':
                username = input("Type your username: ")
                password = getpass.getpass("Type your password: ")
                auth = authinfo.ApiAuth(usertoken=username, password=password)
            else:
                token = input("Paste your auth token: ")
                auth = authinfo.ApiAuth(usertoken=token)

        authinfo.store(auth, args.provider)
        if not args.hostname:
            process_message = "Host name should be provided."
            return EXECUTION_RESULT_NOK, process_message
    # informations arguments
    elif args.usertoken and args.password and args.hostname:
        auth = authinfo.ApiAuth(args.usertoken, args.password)
    elif args.hostname:
        if authinfo.exists(args.provider):
            auth = authinfo.load(args.provider)
        else:
            process_message = "No stored auth information found for " \
                              "provider: '%s'" % args.provider
            return EXECUTION_RESULT_NOK, process_message
    else:  # no arguments
        process_message = "Warning: The hostname to be updated must be " \
                          "provided.\nUsertoken and password can be either " \
                          "provided via command line or stored with --store " \
                          "option.\nExecute noipy --help for more details."
        return EXECUTION_RESULT_NOK, process_message

    updater = UpdaterProvider(auth, args.hostname)

    ip_address = args.ip if args.ip else get_ip()

    print("Updating hostname '%s' with IP address %s ..."
          % (args.hostname, ip_address))

    updater.update_dns(ip_address)
    print(updater.status_message)

    process_message = updater.status_message

    return EXECUTION_RESULT_OK, process_message


def create_parser():
    parser = argparse.ArgumentParser(
        description="Update DDNS IP address on selected provider.")
    parser.add_argument('-u', '--usertoken', help="provider username or token")
    parser.add_argument('-p', '--password', help="provider password when apply")
    parser.add_argument('-n', '--hostname',
                        help="provider hostname to be updated")
    parser.add_argument('--provider', help="DDNS provider plugin",
                        choices=dnsupdater.AVAILABLE_PLUGINS.keys(),
                        default=dnsupdater.DEFAULT_PLUGIN)
    parser.add_argument('--store',
                        help="store DDNS authentication information and "
                             "update the hostname if it is provided",
                        action='store_true')
    parser.add_argument('-c', '--config',
                        help="path to noipy config dir (default: %s)" % DEFAULT_CONFIG_DIR,
                        default=DEFAULT_CONFIG_DIR)
    parser.add_argument('ip', metavar='IP_ADDRESS', nargs='?',
                        help="New host IP address. If not provided, current "
                             "external IP address will be used.")

    return parser


def main():
    print_version()
    parser = create_parser()
    args = parser.parse_args()

    result, status_message = execute_update(args)
    print(status_message)
    if result != EXECUTION_RESULT_OK:
        parser.format_usage()

    sys.exit(result)

if __name__ == '__main__':
    main()
