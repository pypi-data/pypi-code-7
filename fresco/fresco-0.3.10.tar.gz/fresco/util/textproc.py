from unicodedata import normalize, combining


def strip_accents(s):
    """
    Return ``s`` with all accents stripped
    """
    return ''.join(c
                   for c in normalize('NFD', s)
                   if not combining(c))


def plural(quantity, one, multiple, zero=None, two=None):
    """
    Return a singular or plural strings for ``quantity``.

    Synopsis::

        >>> plural(1, '%d item', '%d items')
        '1 item'
        >>> plural(2, '%d item', '%d items')
        '2 items'

    Exceptions for zero and 2 quantities can be specified::

        >>> from functools import partial
        >>> p = partial(plural,
        ...     zero='what bottles?',
        ...     one='one bottle left',
        ...     two='a pair of bottles, hanging on the wall',
        ...     multiple='%d green bottles, hanging on the wall',
        ... )
        >>> for bottles in range(10, -1, -1):
        ...     print p(bottles)
        ...
        10 green bottles, hanging on the wall
        9 green bottles, hanging on the wall
        8 green bottles, hanging on the wall
        7 green bottles, hanging on the wall
        6 green bottles, hanging on the wall
        5 green bottles, hanging on the wall
        4 green bottles, hanging on the wall
        3 green bottles, hanging on the wall
        a pair of bottles, hanging on the wall
        one bottle left
        what bottles?
    """
    if zero is None:
        zero = multiple
    if two is None:
        two = multiple
    if quantity == 0:
        text = zero
    elif quantity == 1:
        text = one
    elif quantity == 2:
        text = two
    else:
        text = multiple

    try:
        return text % (quantity,)
    except TypeError:
        return text
