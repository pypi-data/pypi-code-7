# -*- coding: utf-8 -*-
import wlp_parser


__current_file = None


def setfilebyname(name):
    global __current_file
    __current_file = open(name, 'r')


def setfilebyfd(fd):
    global __current_file
    __current_file = fd


def mkdict():
    dict = {}
    if __current_file is None:
        raise ValueError('current file has not been set.')

    tree = wlp_parser.parser.parse(
        wlp_parser.lexer.lex(__current_file.read()))

    for subtree in tree:
        current_key = subtree[0].getstr().strip('<>')
        if current_key not in dict:
            dict[current_key] = {}

        for key, value in subtree[1]:
            key = key.getstr()
            value = value.getstr().strip("'\"")
            dict[current_key][key] = value

    return dict
