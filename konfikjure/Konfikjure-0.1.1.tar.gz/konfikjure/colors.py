# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of Konfikjure.
# See the file 'docs/LICENSE.txt' for copying permission.

def color(text, color_code):
    return '\x1b[%dm%s\x1b[0m' % (color_code, text)


def yellow(text):
    return color(text, 33)


def purple(text):
    return color(text, 35)
