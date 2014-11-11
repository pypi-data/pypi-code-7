#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.utils.runtime import make_constants, bind_all

import random


class MakeConstants(UTCase):

    def setUp(self):
        self.output = []
        self.stoplist = ['range']

    def verbose(self, message):
        """
        Verbose function to apply when using make_constants
        """

        self.output.append(message)

    def sample(self):

        def sample(population, k):
            "Choose k unique random elements from a population sequence."
            if not isinstance(population, (list, tuple, str)):
                raise TypeError('Cannot handle type', type(population))
            n = len(population)
            if not 0 <= k <= n:
                raise ValueError("sample larger than population")
            result = [None] * k
            pool = list(population)
            for i in range(k):         # invariant:  non-selected at [0,n-i)
                j = int(random.random() * (n - i))
                result[i] = pool[j]
                pool[j] = pool[n - i - 1]
            return result

        return sample

    def _test_verbose(self):

        verbose_message = [
            "isinstance --> {0}".format(isinstance),
            "list --> {0}".format(list), "tuple --> {0}".format(tuple),
            "str --> {0}".format(str), "TypeError --> {0}".format(TypeError),
            "type --> {0}".format(type), "len --> {0}".format(len),
            "ValueError --> {0}".format(ValueError),
            "list --> {0}".format(list),
            #"range --> {0}".format(range),
            "int --> {0}".format(int),
            "random --> {0}".format(random),
            "new folded constant:{0}".format((list, tuple, str)),
            "new folded constant:{0}".format(random.random)
        ]

        self.assertEqual(self.output, verbose_message)

    def test_function(self):

        make_constants(
            verbose=self.verbose, stoplist=self.stoplist)(self.sample())

    def test_class(self):

        class A(object):

            pass

        A.a = self.sample()

        bind_all(A, verbose=self.verbose, stoplist=self.stoplist)

        self._test_verbose()


if __name__ == '__main__':
    main()
