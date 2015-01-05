import rply

__lg = rply.LexerGenerator()
# Add takes a rule name, and a regular expression that defines the rule.
__lg.add("OWNER", r'<[a-zA-Z0-9_.+-]+@[a-zA-Z0-9._-]+>')
__lg.add("VAL", r'[\'`"][a-zA-Z0-9@_+.<>() -]+[\'`"]')
__lg.add("VAR", r'[a-zA-Z0-9_<>-]+[:]?')

__lg.ignore(r"\s+")
__lg.ignore(r'[{}=]+')

lexer = __lg.build()

__pg = rply.ParserGenerator(['OWNER', 'VAL', 'VAR'],
                            cache_id='wlp_parser')

"""
    $accept ::= block $end
    block ::= blockstatement
         | block blockstatement
    blockstatement ::= owner '{' commandline '}'
    commandline ::= command
               | commandline command
    command ::= varpart '=' valpart
    owner ::= OWNERID
    varpart ::= VARID
    valpart ::= VALID
"""


@__pg.production('main : block')
def main(p):
    return p[0]


@__pg.production('block : blockstatement')
def block(p):
    return p


@__pg.production('block : block blockstatement')
def block_blockstatement(p):
    p[0].append(p[1])
    return p[0]


@__pg.production('blockstatement : OWNER commandline')
def blockstatement(p):
    return [p[0], p[1]]


@__pg.production('commandline : command')
def commandline(p):
    return p


@__pg.production('commandline : commandline command')
def commandline_command(p):
    p[0].append(p[1])
    return p[0]


@__pg.production('command : VAR VAL')
def command(p):
    return p


parser = __pg.build()
