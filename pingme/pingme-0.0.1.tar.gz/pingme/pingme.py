"""
pingme - command line client for pingme application.

usage: pingme [-h] [--devices DEVICES] [message]

positional arguments:
  message

optional arguments:
  -h, --help            show this help message and exit
  --devices DEVICES, -d DEVICES
                        Comma delimited list of device ids.

"""
from __future__ import print_function

from six.moves import configparser  # pylint: disable=F0401,E0611
from six.moves.configparser import NoSectionError, MissingSectionHeaderError  # pylint: disable=F0401,E0611
import requests
import argparse
import os

import json

__VERSION__ = "0.1.0"


def send_ping(devices, message):
    """ Send the message to the the ping server.

    :param devices:
    :param message:
    :return: exit(0) if successful otherwise exit(1)
    """
    data = {'device_id': devices, 'message': message}
    headers = {'content-type': 'application/json'}
    response = requests.post('https://ping.blu3f1re.com/ping/', data=json.dumps(data), headers=headers)
    if response.status_code == requests.codes.ok:  # pylint: disable=E1101
        exit(0)
    else:
        print('Server returned error {0}'.format(response.status_code))
        exit(1)


def show_version():
    """ Show version number.

    :return: version string
    """
    return "pingme v{0}".format(__VERSION__)


def parse_args():
    """ Parse the passed in arguments and returns them.

    :return: arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                        help='Show version number', version=show_version())
    parser.add_argument('--devices', '-d',
                        required=False,
                        help='Comma delimited list of device ids.')
    parser.add_argument('message', nargs='?')

    args = vars(parser.parse_args())

    return args


def check_config_file():
    """ Check if the config file exists.

    :return: file path
    """
    home = os.path.expanduser('~')
    file_path = os.path.abspath(home + '/.pingme_config')

    if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
        return file_path
    else:
        return


def read_config_file(fpath):
    """ Read in the config file using ConfigParser.

    :param fpath: File to read
    :return: dictionary of config items
    """
    config = configparser.SafeConfigParser()
    config.read(fpath)

    try:
        options = config.options('Default')
    except (NoSectionError, MissingSectionHeaderError):
        print('Bad config file, header must be "Default"')
        exit(1)

    dict1 = {}

    for option in options:
        dict1[option] = config.get('Default', option)

    return dict1


def config_check(args, config, key):
    """ Take in the args, config, and returns the proper key.

    :param args:
    :param config:
    :param key:
    :return: value
    """
    value = args.get(key)

    if value is None:
        value = config.get(key)

    return value


def main():
    """ The main entry point to the script it parses all the arguments then sends the ping.

    :return: exit(1) if there is an error.
    """
    args = parse_args()
    config = {}

    file_path = check_config_file()

    if file_path:
        config = read_config_file(file_path)

    devices = config_check(args, config, 'devices')
    message = config_check(args, config, 'message')

    if None in [message, devices]:
        print(__doc__)
        exit(1)

    devices = [device for device in devices.split(',')]

    send_ping(devices, message)


if __name__ == '__main__':
    main()
