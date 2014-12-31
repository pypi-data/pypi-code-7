# ======================= QuantGo Copyright Notice ============================
# Copyright 2013 QuantGo, LLC.  All rights reserved.
# Permission to use solely inside a QuantGo Virtual Quant Lab
# Written By: Nikolay
# Date: 12-12.2013
# ======================= QuantGo Copyright Notice ============================

import sys

from schema import commands, main_parser_schema


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
    prog_options = main_parser_schema['main']['properties'].keys() if main_parser_schema['main'].get('properties') else None
    actions_and_options = actions + [('--%s' % n) for n in prog_options]
    prog = 'service'
    action_passed = lambda: [i for i in words if i in actions][0] \
                    if [i for i in words if i in actions] else None
    # complete prog
    if len(words) == 1 and current_word != prog:
        print_choices([prog])
    elif current_word == prog:
        # print prog options + actions
        print_choices(actions_and_options)
    # complete prog options and action
    if len(words) > 1 and words[0] == prog and current_word not in actions \
        and  not action_passed():
        choices = None
        if current_word.startswith('-') and current_word.lstrip('-') not in prog_options:
            choices = [('--%s' % n) for n in prog_options
                       if n.startswith(current_word.lstrip('-'))]
        elif current_word.lstrip('-') not in prog_options:
            choices = [n for n in actions_and_options if n.startswith(current_word)]

        if not choices:
            choices = actions_and_options

        print_choices(choices)

    # complete params
    if len(words) >= 2 and words[0] == prog and action_passed():
        action = action_passed()
        choices = options(action)
        if choices is not None and current_word.startswith('-'):
            choices = [('--%s' % n) for n in choices if n.startswith(current_word[2:])]
            print_choices(choices)
        elif choices is not None:
            choices = [('--%s' % n) for n in choices]
            print_choices(choices)
    print_no_choices()

if __name__ == '__main__':
    if len(sys.argv) == 3:
        complete(sys.argv[1], int(sys.argv[2]))
    else:
        print('usage: %s <cmdline> <point>' % sys.argv[0])
