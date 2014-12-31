# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

"""Cli wrapper."""
# -*- coding: utf-8 -*-
import argparse
import errors
import json
import logging
import os
import sys
from pprint import pprint

import config
from client import ApiClient
from api_schema import commands

logging.basicConfig(level=logging.ERROR)

base = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(base, 'config.py')

type_map = {'array': str,
            'integer': int,
            'boolean': bool,
            'object': str,
            'string': str,
            }


def main_parser(args):
    parser = argparse.ArgumentParser(prog='quantgo', usage='usage: %(prog)s [action | help] [action arguments] [help]',
                                     description='quantgo cli tool allows you to call QNet Query API via commandline interface.',
                                     add_help=False)
    choices = commands.keys()
    choices.append('help')
    parser.add_argument('action', nargs='?', help='Action to query.',
                        choices=choices)
    parser.add_argument('-h', '--help', help='Print command help.', action='store_true')
    args, extra = parser.parse_known_args(args=args)
    if args.action == 'help' or all((args.help, args.action is None)):
        parser.print_help()
        sys.exit(0)
    if args.help and args.action is not None and args.action != 'help':
        extra.append('--help')
    return args.action, extra, parser


def parse_command(action, args):
    command = commands[action]
    usage = '%(prog)s ' + action + ' [options]' + '\n' + command['description']
    parser = argparse.ArgumentParser(usage=usage, add_help=False)
    params = command.get('properties')
    if params:
        for param, param_type in params.items():
            # TODO: add type parsing
            if param_type['type'] == 'array':
                parser.add_argument('--%s' % param,
                                    required=param_type['required'],
                                    type=type_map[param_type['type']],
                                    nargs='*',
                                    help=param_type['description'],
                                    )
            elif param_type['type'] == 'boolean':
                parser.add_argument('--%s' % param,
                                    required=param_type['required'],
                                    action='store_true',
                                    help=param_type['description'],
                                    )
            else:
                if 'enum' in param_type:
                    parser.add_argument('--%s' % param,
                                        required=param_type['required'],
                                        type=type_map[param_type['type']],
                                        choices=param_type['enum'],
                                        help=param_type['description'],
                                        )
                else:
                    parser.add_argument('--%s' % param,
                                        required=param_type['required'],
                                        type=type_map[param_type['type']],
                                        help=param_type['description'],
                                        )
    parser.add_argument('--help', action='help', help='Prints this help message.')
    args, extra = parser.parse_known_args(args=args)
    return args, extra


def main(args):
    action, extra, parser = main_parser(args)
    try:
        params, leftovers = parse_command(action, extra)
    except Exception as e:
        parser.print_help()
        return

    if leftovers:
        raise errors.InvalidParameter('Invalid parameters: %s.' % (leftovers,))

    logging.debug('PARAMS: %r', params)
    msg = '\nYou must either set environment variable {var} or setup ' \
        'config file.\nNOTE: config file path is {confpath}.\n'
    access_key = os.environ.get('QNET_ACCESS_KEY', config.access_key)
    if not access_key:
        print msg.format(var='QNET_ACCESS_KEY', confpath=config_path)
        return
    secret_key = os.environ.get('QNET_SECRET_KEY', config.secret_key)
    if not secret_key:
        print msg.format(var='QNET_SECRET_KEY', confpath=config_path)
        return

    client = ApiClient(access_key=access_key, secret_key=secret_key)
    params = dict((k, v) for k, v in vars(params).items() if v is not None)
    result = client.call(action, **params)
    try:
        result = json.loads(result)
        print json.dumps(result,
                         encoding="ascii",
                         sort_keys=True,
                         indent=4,
                         separators=(',', ': '))
    except ValueError, e:
        logging.error(e)
        pprint(result)


def build_params(args):
    params_dict = {}
    key = None
    for elem in args:
        if elem[0] == '-':
            key = elem.strip('-')
        else:
            if key:
                if key not in params_dict:
                    params_dict[key] = [elem]
                else:
                    params_dict[key].append(elem)
    # revert non list items
    for k, v in params_dict.items():
        if len(v) == 1:
            params_dict[k] = v[0]
    return params_dict
