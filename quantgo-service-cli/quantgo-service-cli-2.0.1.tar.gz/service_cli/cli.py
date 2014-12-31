# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

"""Cli wrapper."""
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import sys

from schema import commands, main_parser_schema
from service import service


logging.basicConfig(level=logging.ERROR)

type_map = {'array': str,
            'integer': int,
            'boolean': bool,
            'object': str,
            'string': str,
            }


def build_parser(parser, schema):
    if schema.get('properties'):
        for param, param_type in schema.get('properties').items():
            if param == 'help':
                parser.add_argument('--%s' % param,
                    help=param_type['description'],
                    action='store_true' if param_type != 'help' else param_type)
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

    # add default help if it hasn't been added
    if not schema.get('properties') or 'help' not in schema.get('properties'):
        parser.add_argument('--help', action='help',
                            help="Print this help message.")

def main_parser(args):

    parser = argparse.ArgumentParser(prog='service',
                    usage=main_parser_schema['main'].get('usage'),
                    description=main_parser_schema['main'].get('description'),
                    add_help=False)
    choices = commands.keys()
    choices.append('help')
    parser.add_argument('action', nargs='?', help='Action to query.',
                        choices=choices, default='help')
    build_parser(parser, main_parser_schema['main'])

    args, extra = parser.parse_known_args(args=args)

    if args.action == 'help' or all((args.help, args.action is None)):
        parser.print_help()
        sys.exit(0)
    if args.help and args.action is not None and args.action != 'help':
        extra.append('--help')
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    return args, extra


def parse_command(action, args):
    schema = commands[action]
    usage = '%(prog)s ' + action + ' [options]' + '\n' + schema['description']
    parser = argparse.ArgumentParser(usage=usage, add_help=False)
    build_parser(parser, schema)

    args, extra = parser.parse_known_args(args=args)
    return args, extra


def print_json(json_blob):
    try:
        result = json.loads(json_blob)
        print json.dumps(result,
                         encoding="ascii",
                         sort_keys=True,
                         indent=4,
                         separators=(',', ': '))
    except ValueError:
        # assuming we got streamed data. not json
        # so just printing its content
        for line in json_blob.splitlines():
            print line


def main(args):
    logging.debug('RAW_ARGS: %r', args)
    main_args, extra = main_parser(args)
    logging.debug('MAIN_ARGS: %r', main_args)
    if not main_args.no_update:
        logging.warning('Currently version verification is not implemented, ' \
                        'skipping it...')
    action = main_args.action
    params, leftovers = parse_command(action, extra)
    logging.debug('ACTION: %r; PARAMS: %r', action, params)
    if leftovers:
        logging.warning('EXTRA params: %r', leftovers)

    client_params = {}
    if main_args.host:
        client_params['host'] = main_args.host
    if main_args.port:
        client_params['port'] = main_args.port


    if not main_args.save_file:
        logging.debug('Using system stdout as stdout.')
        stdout = sys.stdout
    else:
        logging.debug('Using file %s as stdout.', main_args.save_file)
        stdout = open(main_args.save_file, 'wb')

    client_params['stdout'] = stdout

    try:
        service(action, params, **client_params)
    finally:
        stdout.close()

#    result = service(action, params, **client_params)
#    if not main_args.save_file:
#        try:
#            print_json(result)
#        # IOError is produced when user for example pipes output to more
#        # command and closes it before all output is printed. This exception
#        # should be silently passed.
#        except IOError:
#            pass
#    else:
#        with open(main_args.save_file, 'w') as fp:
#            fp.write(result)
