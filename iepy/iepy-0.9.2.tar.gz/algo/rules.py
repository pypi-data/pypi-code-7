# Write here your rules
# RELATION = 'your relation here'

from refo import Star, Any, Plus
from iepy.extraction.rules import rule, Token, Pos

RELATION = "wasborn"


@rule(True)
def born_date_and_death_in_parenthesis(Subject, Object):
    """ Example: Carl Bridgewater (January 2, 1965 - September 19, 1978) was shot dead """
    anything = Star(Any())
    return anything + Subject + anything + Token("was born") + anything + Object + anything
