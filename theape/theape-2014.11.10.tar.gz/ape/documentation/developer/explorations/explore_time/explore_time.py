
# python standard library
import re


DIGIT = r'\d'
ONE_OR_MORE = r"+"
ZERO_OR_MORE = r'*'
DECIMAL = r'\.'
SPACE = r'\s'
SPACES = SPACE + ONE_OR_MORE
OPTIONAL_SPACES = SPACE + ZERO_OR_MORE
OR = r'|'

# groups
NAMED = "(?P<{n}>{e})"
GROUPED = "({0})"

# numbers
INTEGER = DIGIT + ONE_OR_MORE
FLOAT = INTEGER + DECIMAL + INTEGER

REAL = INTEGER + OR + FLOAT

WEEKS = NAMED.format(n='weeks', e=REAL) + OPTIONAL_SPACES + '[wW]'
DAYS = NAMED.format(n='days', e=REAL) + OPTIONAL_SPACES + '[dD]'

# compiled_expressions
DAY_EXPRESSION = re.compile(DAYS)
WEEK_EXPRESSION = re.compile(WEEKS)


example_1 = '2 days 3 hours 10 Weeks'
example_2 =  '1.2Weeks 6.2 days'

match = DAY_EXPRESSION.search(example_1)
print "Days: " + match.group('days')

match = DAY_EXPRESSION.search(example_2)
print 'Days: ' + match.group('days')


match = WEEK_EXPRESSION.search(example_1)
print 'weeks: ' + match.group('weeks')
match = WEEK_EXPRESSION.search(example_2)
print 'Weeks: ' + match.group('weeks')
