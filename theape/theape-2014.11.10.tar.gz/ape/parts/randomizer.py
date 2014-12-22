
# python standard library
from random import choice, randrange, randint
from string import printable, letters, digits


EMPTY_STRING = ''
ALPHA_NUM = letters + digits


class Randomizer(object):
    """
    A class to hold randomizing (static) methods
    """
    @staticmethod
    def string(maximum=100):
        """
        Return a random string composed of printable characters

        :param:

         - `maximum`: Max characters to use

        :return: random printable str of at least 1 and at most maximum characters
        """
        maximum = max(maximum, 1)
        return EMPTY_STRING.join([choice(printable) for ch in range(randrange(1, maximum+1))])

    @staticmethod
    def letters(minimum=1, maximum=100):
        """
        Create a string of upper and lowercase letters

        :param:

         - `minimum`: least amount of characters
         - `maximum`: most characters allowed

        :return: random string of at least 1 and at most maximum characters
        """
        maximum = max(maximum, 1)
        return EMPTY_STRING.join([choice(letters) for ch in range(randrange(minimum, maximum+1))])

    @staticmethod
    def integer(minimum=0, maximum=100):
        """
        Creates a random integer from 0 to 100 (inclusive)

        :return: random integer
        """
        return randint(minimum, maximum)

    @staticmethod
    def letters_complement(source, minimum=1, maximum=100):
        """
        Creates a string of random letters none of which are in source

        :param:

         - `source`: string to complement
         - `minimum`: minimum length of complement
         - `maximum`: maximum length of complement
        """
        complement = []
        for ch in range(randrange(minimum, maximum+1)):
            c = choice(letters)
            if c not in source:
                complement.append(c)
        return EMPTY_STRING.join(complement)

    @staticmethod
    def alphanum(minimum=1, maximum=100):
        """
        Creates a string of random alpha-numeric characters

        :param:

         - `minimum`: minimum number of characters to generate
         - `maximum`: maximum length of string
        :return: string of alpha-numeric characters         
        """
        return ''.join([choice(ALPHA_NUM) for an in range(randrange(minimum, maximum))])



# python standard library
import unittest
from types import IntType, StringType


class TestRandomizer(unittest.TestCase):
    def bounds(self):
        bounds = (randint(-100, 100), randint(-100,100))
        minimum = min(bounds)
        maximum = max(bounds)
        return minimum, maximum

    def test_integer(self):
        """
        Does the randomizer return an integer within bounds?
        """
        minimum, maximum = self.bounds()
        actual = Randomizer.integer(minimum=minimum,
                                           maximum=maximum)
        self.assertGreaterEqual(actual, minimum)
        self.assertLessEqual(actual, maximum)
        self.assertEqual(IntType, type(actual))
        return

    def test_letters(self):
        """
        Does it create a string of (alphabet) letters?
        """
        minimum, maximum = self.bounds()
        actual = Randomizer.letters(randint(minimum, maximum))
        self.assertLessEqual(len(actual), max(1, maximum))
        self.assertEqual(StringType, type(actual))
        for character in actual:
            self.assertIn(character, letters)
        return

    def test_string(self):
        """
        Does it create a string of printable characters?
        """
        minimum, maximum = self.bounds()
        
        actual = Randomizer.string(randint(minimum, maximum))
        self.assertGreaterEqual(len(actual), 1)
        self.assertLessEqual(len(actual), max(1, maximum))
        for character in actual:
            self.assertIn(character, printable)
        return

    def test_letters_complement(self):
        """
        Does it return a random string of letters not in the given
        """
        minimum, maximum = self.bounds()
        start = Randomizer.letters(randint(minimum, maximum))
        complement = Randomizer.letters_complement(start)
        for c in complement:
            self.assertNotIn(c, start)
        return

    def test_alphanum(self):
        """
        Does it return a random alpha-numeric string?
        """
        string = Randomizer.alphanum()
        for c in string:
            self.assertIn(c, letters + digits)
        return

