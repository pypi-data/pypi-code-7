# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import string

# Charsets for code 39
REF = (tuple(string.digits) + tuple(string.ascii_uppercase) +
       ('-', '.', ' ', '$', '/', '+', '%'))
B = '1'
E = '0'
CODES = (
    '101000111011101', '111010001010111', '101110001010111',
    '111011100010101', '101000111010111', '111010001110101',
    '101110001110101', '101000101110111', '111010001011101',
    '101110001011101', '111010100010111', '101110100010111',
    '111011101000101', '101011100010111', '111010111000101',
    '101110111000101', '101010001110111', '111010100011101',
    '101110100011101', '101011100011101', '111010101000111',
    '101110101000111', '111011101010001', '101011101000111',
    '111010111010001', '101110111010001', '101010111000111',
    '111010101110001', '101110101110001', '101011101110001',
    '111000101010111', '100011101010111', '111000111010101',
    '100010111010111', '111000101110101', '100011101110101',
    '100010101110111', '111000101011101', '100011101011101',
    '100010001000101', '100010001010001', '100010100010001',
    '101000100010001',
)

EDGE = '100010111011101'
MIDDLE = '0'

# MAP for assigning every symbol (REF) to (reference number, barcode)
MAP = dict(zip(REF, enumerate(CODES)))
