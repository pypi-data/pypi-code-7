
"""Emulation of Django's Q objects.
"""

# pylint: disable=R0903,C0111
# R0903: Too few public methods

import htmlentitydefs
from genconn import quote_list
from dk.orm.marker import marker


__all__ = ['Q']


def escape_char(unichar):
    "Escape unicode characters that have &xx; codes."
    if len(unichar) > 1 and (unichar[0] == '&' and unichar[-1] == ';'):
        return str(unichar)

    o = ord(unichar)
    t = htmlentitydefs.codepoint2name.get(o, o)
    if t == o:
        if 0 < t < 128:
            return str(unichar)
        else:
            return ''
    else:
        return '&' + t + ';'


def escaped_array(s):
    """Convert unicode string to list of ascii characters or
       entitydefs like &oslash; etc.
    """
    return [escape_char(ch) for ch in s]


def charref_escape(s, enc=None):
    """Convert string s (potentially unicode) to a ascii string
       with entitydefs like &oslash; &aelig; etc.
    """
    if s is None:
        return ''
    if not isinstance(s, unicode):
        if enc is not None:
            s = s.decode(enc)
    return ''.join(escape_char(c) for c in s)


def wildcard_escape(val):
    if isinstance(val, unicode):
        res = []
        for ch in val:
            if 0 < ord(ch) < 128:
                res.append(str(ch))
            else:
                res.append('__')
        return ''.join(res)
    return str(val)


def _handle_uc(val):
    if isinstance(val, unicode):
        res = []
        for ch in val:
            try:
                res.append(str(ch))
            except:
                res.append('__')
        return ''.join(res)
    return str(val)


class q_empty(object):
    "Empty start element."
    def __init__(self):
        self.params = []

    def __and__(self, other):
        return other

    def __or__(self, other):
        return other

    def render(self, env):
        return ''

    def __repr__(self):
        return self.render(lambda x:x)

    def __len__(self):
        return 0


class qobj(object):
    "abstract base class"
    def __and__(self, other):
        return q_and(self, other)

    def __or__(self, other):
        return q_or(self, other)

    def render(self, env):
        return 'Error:qobj'

    def __repr__(self):
        return self.render(lambda x:x)

    @property
    def params(self):  # pylint:disable=R0201
        return []

    def __len__(self):
        return 1


class q_isnull(qobj):
    """foo__isnull=True  => foo is null
       foo__isnull=False => foo is not null
    """
    def __init__(self, lhs, rhs):
        super(q_isnull, self).__init__()
        self.lhs = lhs
        self.isnull = bool(rhs)

    #def __repr__(self):
    #    test = 'is' if self.isnull else 'is not'
    #    return '(%s %s null)' % (self.lhs, test)

    def render(self, env):
        test = 'is' if self.isnull else 'is not'
        return '(%s %s null)' % (env(self.lhs), test)

class binop(qobj):
    "abstract base class"
    def __init__(self, lhs, rhs, rhsval=None):
        super(binop, self).__init__()
        self.lhs = lhs
        self.rhs = rhs
        self.rhsval = rhsval

    def render(self, env):
        # pylint: disable=E1101
        # E1101: self has no operator, but all relevant subclasses do.
        return '(%s %s %s)' % (env(self.lhs), self.operator, env(self.rhs))
    
    @property
    def params(self):
        return self.lhs.params + self.rhs.params


class param_binop(binop):
    "parameterized binary operation"
    def __init__(self, lhs, rhs):
        super(param_binop, self).__init__(lhs, marker(rhs), rhsval=rhs)
        self._params = [rhs]

    @property
    def params(self):
        return self._params


class q_year(qobj):
    "Extract year part."
    def __init__(self, name, param):
        super(q_year, self).__init__()
        self.name = name
        self.param = param

    def render(self, env):
        return "year(%s) = %s" % (env(self.name), self.param)


class q_month(q_year):
    "Extract month part."
    def render(self, env):
        return "month(%s) = %s" % (env(self.name), self.param)


class q_day(q_year):
    "Extract day part."
    def render(self, env):
        return "day(%s) = %s" % (env(self.name), self.param)

    
class q_eq(param_binop):
    "equal"
    operator = '='

    @property
    def params(self):
        if (isinstance(self.rhsval, unicode) and
            wildcard_escape(self.rhsval) != self.rhsval):
            return [wildcard_escape(self.rhsval), charref_escape(self.rhsval)]
        else:
            return self._params
    
    def render(self, env):
        if isinstance(self.rhsval, unicode):
            if wildcard_escape(self.rhsval) != self.rhsval:
                #escval = charref_escape(self.rhsval)
                return '(%s like %%s and dbo.dk_lat1(%s) = %%s)' % (
                    env(self.lhs), env(self.lhs))
        return super(q_eq, self).render(env)
        

class q_neq(param_binop):
    "not equal operator"
    operator = '<>'


class q_lt(param_binop):
    "less than"
    operator = '<'


class q_gt(param_binop):
    "greater than"
    operator = '>'


class q_lte(param_binop):
    "less or equal"
    operator = '<='


class q_gte(param_binop):
    "greater or equal"
    operator = '>='
    

class q_and(binop):
    "and operator"
    operator = 'and'


class q_or(binop):
    "or operator"
    operator = 'or'


class q_contains(param_binop):
    "field like '%val%'"
    operator = 'like'

    def __init__(self, field, val):
        super(q_contains, self).__init__(field, '%' + _handle_uc(val) + '%')
       

class q_startswith(q_contains):
    "field like 'val%'"
    def __init__(self, field, val):
        super(q_startswith, self).__init__(field, _handle_uc(val) + '%')


class q_endswith(q_contains):
    "field like '%val'"
    def __init__(self, field, val):
        super(q_endswith, self).__init__(field, '%' + _handle_uc(val))


class q_like(q_contains):
    "field like 'val'"
    def __init__(self, field, val):
        super(q_like, self).__init__(field, _handle_uc(val))
    

q_icontains = q_contains


class q_in(qobj):
    "field in (...)"
    def __init__(self, field, lst):
        super(q_in, self).__init__()
        self.field = field
        self.lst = lst

    def render(self, env):
        if len(self.lst) == 0:
            return "%s in (null)" % env(self.field)
        return "%s in (%s)" % (env(self.field), quote_list(tuple(self.lst)))


def Q(qObj=None, **kw):
    res = q_empty()
    if qObj is not None:
        res &= qObj
        
    for fieldspec, param in kw.items():
        if '__' not in fieldspec:
            res &= q_eq(fieldspec, param)
        else:
            name, op = fieldspec.split('__')
            res &= globals()['q_' + op](name, param)

    return res
