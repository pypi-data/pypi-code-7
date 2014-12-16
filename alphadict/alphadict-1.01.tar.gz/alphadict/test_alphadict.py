from unittest import TestCase
from collections import OrderedDict
from alpha_dict import AlphaDict
from random import choice
import string
import hashlib


class AlphaDictTestCase(TestCase):

    def test_correctly_sorted(self):

        guts = (
            ('a', choice(string.digits)),
            ('b', choice(string.digits)),
            ('c', choice(string.digits)),
            ('thing', OrderedDict((
                ('a', choice(string.digits)),
                ('b', choice(string.digits)),
                ('c', choice(string.digits)),
                ('d', [
                    OrderedDict((
                        ('a', choice(string.digits)),
                        ('b', choice(string.digits)),
                        ('c', choice(string.digits)),
                    )),
                    OrderedDict((
                        ('a', choice(string.digits)),
                        ('b', choice(string.digits)),
                        ('c', choice(string.digits)),
                    )),
                    OrderedDict((
                        ('a', choice(string.digits)),
                        ('b', choice(string.digits)),
                        ('c', choice(string.digits)),
                    )),
                    [
                        OrderedDict((
                            ('a', choice(string.digits)),
                            ('b', choice(string.digits)),
                            ('c', choice(string.digits)),
                        ))
                    ],
                    [
                        OrderedDict((
                            ('a', choice(string.digits)),
                            ('b', choice(string.digits)),
                            ('c', choice(string.digits)),
                        ))
                    ],
                    ]),
                ('thing', OrderedDict((
                    ('a', choice(string.digits)),
                    ('b', choice(string.digits)),
                    ('c', choice(string.digits)),
                )))
            )))
        )

        self.assertEqual(AlphaDict(guts), OrderedDict(guts))

    def test_incorrectly_sorted(self):
        guts = (
            ('a', choice(string.digits)),
            ('b', choice(string.digits)),
            ('c', choice(string.digits)),
            ('thing', OrderedDict((
                ('a', choice(string.digits)),
                ('b', choice(string.digits)),
                ('c', choice(string.digits)),
                ('d', [
                    OrderedDict((
                        ('a', choice(string.digits)),
                        ('b', choice(string.digits)),
                        ('c', choice(string.digits)),
                    )),
                    OrderedDict((
                        ('a', choice(string.digits)),
                        ('b', choice(string.digits)),
                        ('c', choice(string.digits)),
                    )),
                    OrderedDict((
                        ('a', choice(string.digits)),
                        ('b', choice(string.digits)),
                        ('c', choice(string.digits)),
                    )),
                    [
                        OrderedDict((
                            ('a', choice(string.digits)),
                            ('b', choice(string.digits)),
                            ('c', choice(string.digits)),
                        ))
                    ],
                    [
                        OrderedDict((
                            ('b', choice(string.digits)),
                            ('a', choice(string.digits)),
                            ('c', choice(string.digits)),
                        )),
                        OrderedDict((
                            ('a', choice(string.digits)),
                            ('b', choice(string.digits)),
                            ('c', choice(string.digits)),
                        ))
                    ],
                ]),
                ('thing', OrderedDict((
                    ('a', choice(string.digits)),
                    ('b', choice(string.digits)),
                    ('c', choice(string.digits)),
                )))
            )))
        )
        self.assertNotEqual(AlphaDict(guts), OrderedDict(guts))

    def test_first_level_correction(self):
        a = AlphaDict((
            ('b', 1),
            ('a', 1),
            ('c', 1),
        ))
        b = OrderedDict((
            ('a', 1),
            ('b', 1),
            ('c', 1),
        ))
        self.assertEqual(a, b)

    def test_second_level_correction(self):
        a = AlphaDict((
            ('b', 1),
            ('a', OrderedDict((
                ('b', 1),
                ('a', 1),
                ('c', 1),
            ))),
            ('c', 1),
        ))
        b = OrderedDict((
            ('a', OrderedDict((
                ('a', 1),
                ('b', 1),
                ('c', 1),
            ))),
            ('b', 1),
            ('c', 1),
        ))
        self.assertEqual(a, b)

    def test_list_dict_correction(self):
        a = AlphaDict((
            ('a', [
                OrderedDict((
                    ('b', 1),
                    ('a', 1),
                    ('c', 1),
                )),
                OrderedDict((
                    ('c', 1),
                    ('a', 1),
                    ('b', 1),
                )),
                OrderedDict((
                    ('a', 1),
                    ('b', 1),
                    ('c', 1),
                ))
            ]),
        ))
        b = OrderedDict((
            ('a', [
                OrderedDict((
                    ('a', 1),
                    ('b', 1),
                    ('c', 1),
                )),
                OrderedDict((
                    ('a', 1),
                    ('b', 1),
                    ('c', 1),
                )),
                OrderedDict((
                    ('a', 1),
                    ('b', 1),
                    ('c', 1),
                ))
            ]),
        ))
        self.assertEqual(a, b)

    def test_key_delete(self):
        a = AlphaDict((
            ('a', [
                OrderedDict((
                    ('a', 1),
                    ('b', 1),
                    ('c', 1),
                )),
            ]),
            ('b', [
                OrderedDict((
                    ('b', 1),
                    ('a', 1),
                    ('c', 1),
                )),
            ]),
        ))
        del a['a']
        b = OrderedDict((
            ('b', [
                OrderedDict((
                    ('a', 1),
                    ('b', 1),
                    ('c', 1),
                )),
            ]),
        ))
        self.assertEqual(a, b)

    def test_hash(self):
        a = OrderedDict((
            ('a', [
                OrderedDict((
                    ('a', 1),
                    ('c', 1),
                    ('b', 1),
                )),
            ]),
        ))
        b = OrderedDict((
            ('a', [
                OrderedDict((
                    ('c', 1),
                    ('b', 1),
                    ('a', 1),
                )),
            ]),
        ))
        self.assertNotEqual(a, b)

        a = AlphaDict(a)
        b = AlphaDict(b)
        self.assertEqual(a, b)

        hash_a = hashlib.md5(str(a)).hexdigest()
        hash_b = hashlib.md5(str(b)).hexdigest()
        self.assertEqual(hash_a, hash_b)

