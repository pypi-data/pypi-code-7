from modgrammar import *
from modgrammar.extras import *
from modgrammar.util import *

grammar_whitespace_mode = 'explicit'


class HHMMSSTimeComponent(Grammar):
    grammar = REPEAT(WORD('[0-9]'), count=2)


class HHMMSSTimeHourComponent(HHMMSSTimeComponent):
    grammar_name = "Hour"


class HHMMSSTimeMinuteComponent(HHMMSSTimeComponent):
    grammar_name = "Minute"


class HHMMSSSecondComponent(HHMMSSTimeComponent):
    grammar_name = "Second"


class HHMMSSHundredthsComponent(HHMMSSTimeComponent):
    grammar_name = "Second"


class HHMMSSTime(Grammar):
    grammar = (HHMMSSTimeHourComponent, ':', HHMMSSTimeMinuteComponent, ':', HHMMSSSecondComponent, OPTIONAL('.', HHMMSSHundredthsComponent))


class UnixTime(Grammar):
    grammar = (WORD('[0-9]', count=10),)


class Time (Grammar):
    grammar = (HHMMSSTime | UnixTime)


class Text(Terminal):
    # matches:
    #  any character except # or <
    #  # if there is a \ right before it
    #  < if there is a \ right before it
    #  no space at the end (" foo asd " => " foo asd")
    grammar = (RE(r'( *(\\#|\\<|[^#< ])+)+'),)


class Link (Grammar):
    grammar = ('<', REPEAT(ANY), '>')
    grammar_name = "Link"


class Tag (Grammar):
    grammar = ('#', WORD('A-Za-z0-9'))


class Indentation (Grammar):
    grammar = ('-',)


class MuchSpace (Grammar):
    grammar = (ONE_OR_MORE(' '),)
    grammar_collapse = True


class OMuchSpace (Grammar):
    grammar = (ZERO_OR_MORE(' '),)
    grammar_collapse = True


class Line (Grammar):
    grammar = (ZERO_OR_MORE(Indentation), OMuchSpace,
               OPTIONAL(Time, MuchSpace),
               OMuchSpace, Text, OMuchSpace,
               OPTIONAL(Link),
               ZERO_OR_MORE(MuchSpace, Tag))
