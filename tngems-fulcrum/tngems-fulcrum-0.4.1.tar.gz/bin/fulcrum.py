#!/usr/bin/env python3
import sys;del sys.path[0]
import os

from libtng.cli.baseparser import parser


COMMANDS = [
    'fulcrum.controllers.cli.renderdb',
    'fulcrum.controllers.cli.dbshell',
    'fulcrum.controllers.cli.shell',
    #'fulcrum.cli.shell',
]


if __name__ == '__main__':
    parser.register_commands(COMMANDS)
    if not COMMANDS:
        print("No commands available.", file=sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    try:
        func = args.func
    except AttributeError:
        print("Specify a subcommand.", file=sys.stderr)
        sys.exit(1)
    else:
        sys.exit(func(args))
   
