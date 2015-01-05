#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
import wlp_parser

from rply import Token
import whitelist
import wlp


# logging.basicConfig(level=logging.DEBUG)

EXPECTED_WL = {
    'alfarano@students.cs.unibo.it': {
        'From:': 'Cosimo Alfarano',
        'X-Firstname:': 'Cosimo'
    },
    'kame@innocent.com': {
        'From:': 'kame@inwind.it',
        'Reply-to': 'me',
        'Reply-to:': 'KA',
        'Sender:': 'Kalfa'
    }
}


class TestWLP(unittest.TestCase):
    maxDiff = None
    test_input = '''<kame@innocent.com> {
                From: = 'ME' Sender: = "Cosimo" Reply-to = "me"
            }

            <alfarano@students.cs.unibo.it> {
                From: = 'Cosimo Alfarano'
                X-Firstname: = 'Cosimo'
            }

            <kame@innocent.com> {
                From: = 'kame@inwind.it'
                Reply-to: = "KA"
                Sender: = "Kalfa"
            }'''

    def test_wlp_lexer(self):
        expected_stream = [
            Token('OWNER', '<kame@innocent.com>'),
            Token('VAR', 'From:'),
            Token('VAL', "'ME'"),
            Token('VAR', 'Sender:'),
            Token('VAL', '"Cosimo"'),
            Token('VAR', 'Reply-to'),
            Token('VAL', '"me"'),
            Token('OWNER', '<alfarano@students.cs.unibo.it>'),
            Token('VAR', 'From:'),
            Token('VAL', "'Cosimo Alfarano'"),
            Token('VAR', 'X-Firstname:'),
            Token('VAL', "'Cosimo'"),
            Token('OWNER', '<kame@innocent.com>'),
            Token('VAR', 'From:'),
            Token('VAL', "'kame@inwind.it'"),
            Token('VAR', 'Reply-to:'),
            Token('VAL', '"KA"'),
            Token('VAR', 'Sender:'),
            Token('VAL', '"Kalfa"')
        ]
        tokens = list(wlp_parser.lexer.lex(self.test_input))
        self.assertEqual(tokens, expected_stream)

    def test_wlp_parser(self):
        expected_tree = [
            [
                Token('OWNER', '<kame@innocent.com>'),
                [
                    [Token('VAR', 'From:'), Token('VAL', "'ME'")],
                    [Token('VAR', 'Sender:'), Token('VAL', '"Cosimo"')],
                    [Token('VAR', 'Reply-to'), Token('VAL', '"me"')]
                ]
            ],
            [
                Token('OWNER', '<alfarano@students.cs.unibo.it>'),
                [
                    [Token('VAR', 'From:'), Token('VAL', "'Cosimo Alfarano'")],
                    [Token('VAR', 'X-Firstname:'), Token('VAL', "'Cosimo'")]
                ]
            ],
            [
                Token('OWNER', '<kame@innocent.com>'),
                [
                    [Token('VAR', 'From:'), Token('VAL', "'kame@inwind.it'")],
                    [Token('VAR', 'Reply-to:'), Token('VAL', '"KA"')],
                    [Token('VAR', 'Sender:'), Token('VAL', '"Kalfa"')]
                ]
            ]
        ]
        lex_stream = wlp_parser.lexer.lex(self.test_input)
        tree = wlp_parser.parser.parse(lex_stream)
        self.assertEqual(tree, expected_tree)

    def test_wlp(self):
        wlp.setfilebyname('examples/whitelist.example')
        wl_dict = wlp.mkdict()
        self.assertEqual(wl_dict, EXPECTED_WL)


class TestWhitelist(unittest.TestCase):
    def setUp(self):
        self.wl = whitelist.whitelist('examples/whitelist.example')

    def test_init(self):
        self.assertEqual(self.wl.wl, EXPECTED_WL)

    def test_checkfrom(self):
        self.assertEqual(self.wl.checkfrom('kame@inwind.it'),
                         'kame@innocent.com')

if __name__ == "__main__":
    unittest.main()
