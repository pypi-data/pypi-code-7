
import string


# the class-based expressions are mostly for organization
# but sometimes they're just too clunky
LEFT_BRACKET = '['
RIGHT_BRACKET = ']'


class FormalDefinition(object):
    """
    The basic operators and elements of a regular expression
    """
    empty_string = '^$'
    alternative = '|'
    OR = alternative
    kleene_star = "*"


class Group(object):
    """
    The Group helps with regular expression groups
    """
    __slots__ = ()

    @staticmethod
    def group(expression):
        """
        Create a grouped expression

        :param:

         - `expression`: the regular expression to group
        :return: uncompiled group expression for e
        """
        return "({e})".format(e=expression)

    @staticmethod
    def named(name, expression):
        """
        Creates a named group

        :param:

         - `name`: name to give the group
         - `expression`: expression to use in the group
        """
        return "(?P<{n}>{e})".format(n=name,
                                     e=expression)

    @staticmethod
    def followed_by(suffix):
        """
        Creates the expression to match if followed by the suffix
        """
        return "(?={0})".format(suffix)

    @staticmethod
    def not_followed_by(suffix):
        """
        Creates a (perl) negative lookahead expression

        e.g. 'alpha(?!beta)' matches 'alpha' and 'alphagamma', not 'alphabeta'

        :param:

           - `suffix`: suffix to avoid matching
        """
        return "(?!{s})".format(s=suffix)

    @staticmethod
    def preceded_by(prefix):
        """
        Creates a look-behind expression

        :param:

         - `prefix`: an expression of fixed-order (no quantifiers or alternatives of different length)
        """
        return "(?<={0})".format(prefix)
    
    @staticmethod
    def not_preceded_by(prefix):
        """
        Creates a (perl) negative look behind expression

        :param:

         - `prefix`: expression to group
        """
        return "(?<!{e})".format(e=prefix)


class Quantifier(object):
    """
    A class to hold cardinality helpers
    """
    __slots__ = ()

    @staticmethod
    def one_or_more(pattern):
        """
        Adds the one-or-more quantifier to the end of the pattern.
        """
        return '{0}+'.format(pattern)    

    @staticmethod
    def zero_or_one(pattern):
        """
        Adds the zero-or-one quantifier to the pattern
        """
        return '{0}?'.format(pattern)

    @staticmethod
    def exactly(repetitions):
        """
        Creates suffix to match source repeated exactly n times

        :param:

         - `repetitions`: number of times pattern has to repeat to match
        """
        return "{{{0}}}".format(repetitions)

    @staticmethod
    def zero_or_more(pattern):
        """
        Adds the kleene star to the pattern

        :return: pattern*
        """
        return "{0}*".format(pattern)

    @staticmethod
    def m_to_n(m, n):
        """
        Creates a repetition ranges suffix {m,n}
        
        :param:

        - `m`: the minimum required number of matches
        - `n`: the maximum number of  matches
        """
        return "{{{m},{n}}}".format(m=m, n=n)


class CharacterClass(object):
    """
    A class to help with character classes
    """
    __slots__ = ()

    alpha_num = r"\w"
    alpha_nums = Quantifier.one_or_more(alpha_num)
    digit = r'\d'
    non_digit = r'\D'
    non_zero_digit = r"[1-9]"

    @staticmethod
    def character_class(characters):
        """
        Creates a character class from the expression

        :param:

         - `characters`: string to convert to a class

        :return: expression to match any character in expression
        """
        return "[{e}]".format(e=characters)

    @staticmethod
    def not_in(characters):
        """
        Creates a complement character class

        :param:

         - `characters`: characters to not match

        :return: expression to match any character not in expression
        """
        return "[^{e}]".format(e=characters)


class Boundaries(object):
    """
    A class to hold boundaries for expressions
    """
    __slots__ = ()

    string_start = "^"
    string_end = "$"

    @staticmethod
    def word(word):
        """
        Adds word boundaries to the word

        :param:

         - `word`: string to add word boundaries to

        :return: string (raw) with word boundaries on both ends
        """
        return r"\b{e}\b".format(e=word)

    @staticmethod
    def string(string):
        """
        Adds boundaries to only match an entire string

        :param:

         - `string`: string to add boundaries to

        :return: expression that only matches an entire line of text
        """
        return r"^{e}$".format(e=string)


class CommonPatterns(object):
    """
    The common patterns that were leftover
    """
    __slots__ = ()
    #anything and everything
    anything = r"."
    everything = Quantifier.zero_or_more(anything)
    letter = CharacterClass.character_class(characters=string.ascii_letters)
    letters = Quantifier.one_or_more(letter)
    optional_letters = Quantifier.zero_or_more(letter)
    space = r'\s'
    spaces = Quantifier.one_or_more(space)
    optional_spaces = Quantifier.zero_or_more(space)
    not_space = r'\S'
    not_spaces = Quantifier.one_or_more(not_space)


class Numbers(object):
    """
    A class to hold number-related expressions
    """
    __slots__ = ()
    
    decimal_point = r'\.'
    single_digit = Boundaries.word(CharacterClass.digit)
    digits = Quantifier.one_or_more(CharacterClass.digit)
    two_digits = Boundaries.word(CharacterClass.non_zero_digit + CharacterClass.digit)
    one_hundreds = Boundaries.word("1" + CharacterClass.digit * 2)
    optional_digits = Quantifier.zero_or_more(CharacterClass.digit)
    # python considers string-start and whitespace to be different lengths
    # so to avoid '.' (which is a word-boundary character) and use line-starts and ends
    # and whitespace requires four alternatives
    START_PREFIX = Group.preceded_by(Boundaries.string_start)
    END_SUFFIX = Group.followed_by(Boundaries.string_end)
    SPACE_PREFIX = Group.preceded_by(CommonPatterns.space)
    SPACE_SUFFIX = Group.followed_by(CommonPatterns.space)
    # Zero
    ZERO = '0'
    zero = (START_PREFIX + ZERO + END_SUFFIX +FormalDefinition.OR +
            START_PREFIX + ZERO + SPACE_SUFFIX +FormalDefinition.OR +
            SPACE_PREFIX + ZERO + END_SUFFIX +FormalDefinition.OR +
            SPACE_PREFIX + ZERO + SPACE_SUFFIX)
    # positive integer
    z_plus = CharacterClass.non_zero_digit + optional_digits
    positive_integer = (START_PREFIX + z_plus + END_SUFFIX +FormalDefinition.OR +
                        START_PREFIX + z_plus + SPACE_SUFFIX +FormalDefinition.OR +
                        SPACE_PREFIX + z_plus + END_SUFFIX +FormalDefinition.OR +
                        SPACE_PREFIX + z_plus + SPACE_SUFFIX )

    nonnegative_integer = (CharacterClass.non_zero_digit + optional_digits +
                           r'\b' +FormalDefinition.OR + 
                            Boundaries.word('0'))
    # this disqualifies leading decimal points but not zeros
    integer = (Group.not_preceded_by(decimal_point) +
                               Quantifier.zero_or_one('-') + 
                               CharacterClass.non_zero_digit + optional_digits +
                               FormalDefinition.OR + 
                               Boundaries.word('0'))

    real = (Quantifier.zero_or_one('-') + 
            CharacterClass.digit + optional_digits +
            decimal_point + optional_digits + 
            FormalDefinition.OR + integer)
    
    HEX = CharacterClass.character_class(string.hexdigits)
    hexadecimal = Quantifier.one_or_more(HEX)



class Networking(object):
    """
    Holds expressions to help with networking-related text.
    """
    __slots__ = ()
    octet = Group.group(expression=FormalDefinition.OR.join([Numbers.single_digit,
                                                             Numbers.two_digits,
                                                             Numbers.one_hundreds,
                                                             Boundaries.word("2[0-4][0-9]"),
                                                             Boundaries.word("25[0-5]")]))

    dot = Numbers.decimal_point

    ip_address = dot.join([octet] * 4)

    hex_pair =  Numbers.HEX + Quantifier.exactly(2)
    mac_address = ":".join([hex_pair] * 6)



