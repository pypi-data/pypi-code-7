# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

import sys

from api_schema import commands


def print_choices(choices):
    print('\n'.join(choices))
    sys.exit(0)


def print_no_choices():
    sys.exit(0)


def complete(cmdline, point):
    schema = commands
    words = cmdline[0:point].split()
    current_word = words[-1]
    actions = schema.keys()
    options = lambda x: schema[x]['properties'].keys() if schema[x].get('properties') else None
    prog = 'quantgo'
    # complete prog
    if len(words) == 1 and current_word != prog:
        print_choices([prog])
    elif current_word == prog:
        print_choices(actions)
    # complete action
    if len(words) == 2 and words[0] == prog and words[1] not in actions:
        choices = [n for n in actions if n.startswith(current_word)]
        print_choices(choices)
    # complete params
    if len(words) > 2 and words[0] == prog and words[1] in actions:
        action = words[1]
        choices = options(action)
        if choices is not None and current_word.startswith('-'):
            choices = [('--%s' % n) for n in choices if n.startswith(current_word[2:])]
            print_choices(choices)
        else:
            print_no_choices()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        complete(sys.argv[1], int(sys.argv[2]))
    else:
        print('usage: %s <cmdline> <point>' % sys.argv[0])
