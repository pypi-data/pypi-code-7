#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.utils.reflect import base_elts, find_embedding

from inspect import getmodule


class BaseEltsTest(UTCase):
    """
    Test base_elts function
    """

    def test_not_inherited(self):
        """
        Test with a not inherited element.
        """

        bases = base_elts(None)
        self.assertFalse(bases)

    def test_function(self):
        """
        Test function
        """

        bases = base_elts(lambda: None)
        self.assertFalse(bases)

    def test_class(self):
        """
        Test class
        """

        class A:
            pass

        class B(A, dict):
            pass

        bases = base_elts(B)
        self.assertEqual(bases, list(B.__bases__) + [object])

    def test_method(self):
        """
        Test method
        """

        class A:
            def a(self):
                pass

        class B(A):
            pass

        bases = base_elts(B.a, cls=A)
        self.assertEqual(len(bases), 1)
        base = bases.pop()
        self.assertEqual(base, A.a)

    def test_not_method(self):
        """
        Test when method has been overriden
        """

        class A:
            def a(self):
                pass

        class B(A):
            def a(self):
                pass

        bases = base_elts(B.a, cls=A)
        self.assertFalse(bases)

    def test_boundmethod(self):
        """
        Test bound method
        """

        class Test:
            def test(self):
                pass

        test = Test()

        bases = base_elts(test.test)
        self.assertEqual(len(bases), 1)
        self.assertEqual(bases.pop(), Test.test)

    def test_not_boundmethod(self):
        """
        Test with a bound method which is only defined in the instance
        """

        class Test:
            def test(self):
                pass

        test = Test()
        test.test = lambda self: None

        bases = base_elts(test.test)
        self.assertFalse(bases)


class FindEmbeddingTest(UTCase):

    def test_none(self):

        embedding = find_embedding(None)

        self.assertFalse(embedding)

    def test_wrong_embedding(self):

        embedding = find_embedding(None, embedding=FindEmbeddingTest)

        self.assertFalse(embedding)

    def test_module(self):

        FindEmbeddingTestModule = getmodule(FindEmbeddingTest)
        embedding = find_embedding(FindEmbeddingTestModule)

        self.assertEqual(len(embedding), 1)
        self.assertIs(FindEmbeddingTestModule, embedding[0])

    def test_function(self):

        embedding = find_embedding(find_embedding)

        self.assertEqual(len(embedding), 2)
        self.assertIs(embedding[0], getmodule(find_embedding))
        self.assertIs(embedding[1], find_embedding)

    def test_class(self):

        embedding = find_embedding(FindEmbeddingTest)

        self.assertEqual(len(embedding), 2)
        self.assertIs(getmodule(FindEmbeddingTest), embedding[0])
        self.assertIs(FindEmbeddingTest, embedding[1])

    def test_method(self):

        embedding = find_embedding(FindEmbeddingTest.test_method)

        self.assertEqual(len(embedding), 3)
        self.assertIs(getmodule(FindEmbeddingTest), embedding[0])
        self.assertIs(FindEmbeddingTest, embedding[1])
        self.assertEqual(FindEmbeddingTest.test_method, embedding[2])

if __name__ == '__main__':
    main()
