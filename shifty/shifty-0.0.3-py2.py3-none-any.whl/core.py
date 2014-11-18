#    -*- coding: utf-8 -*-

"""
module attributes:
    SHIFT_LEFT
    SHIFT_RIGHT
    shift_right
    shift_left
    shift
"""


SHIFT_LEFT = 'left'
SHIFT_RIGHT = 'right'


def shift_right(a, count, in_place=False):
    """
    Shift the iterable 'a' 'count' places to the right.
    The shift is modulo the length of the array.
    Convenience method that wraps shifty.shift()
    :param a: The iterable to shift
    :param count: The number of places to shift
    :param in_place: True: Perform the operation in-place, (False-default).
    :return: The shifted iterable.

    eg:
    >>> a = [1, 2, 3, 4]
    >>> b = shift_right(a, 3)
    >>> b
    [2, 3, 4, 1]
    >>> assert a is not b

    >>> b = shift_right(a, 2, in_place=True)
    >> assert a is b

    >>> b = shift_right(a, 5)
    >>> b
    [2, 3, 4, 1]
    """
    return shift(a, count, in_place=in_place, direction=SHIFT_RIGHT)


def shift_left(a, count, in_place=False):
    """
    Shift the iterable 'a' 'count' places to the left.
    The shift is modulo the length of the array.
    Convenience method that wraps shifty.shift()
    :param a: The iterable to shift
    :param count: The number of places to shift
    :param in_place: True: Perform the operation in-place, (False-default).
    :return: The shifted iterable.

    eg:
    >>> a = [1, 2, 3, 4]
    >>> b = shift_left(a, 3)
    >>> b
    [4, 1, 2, 3]
    >>> assert a is not b

    >>> b = shift_left(a, 2, in_place=True)
    >> assert a is b

    >>> b = shift_left(a, 5)
    >>> b
    [2, 3, 4, 1]
    """
    return shift(a, count, in_place=in_place, direction=SHIFT_LEFT)


def shift(a, count, in_place=False, direction=SHIFT_RIGHT):
    """
    Shift a sliceable iterable 'a', abs('count') places to the right. If the shift is greater than the length of the array,
    then the shift is the modulo of the shift wrt the length of the iterable.
    :type a: list, the input list to shift.
    :type count: int, The number of places to shift.
    :return: The modified iterable.
    """
    count = abs(count)
    if count:
        count = count % len(a)
        if direction == SHIFT_LEFT:
            if in_place:
                for x in xrange(count):
                    a.append(a.pop(0))
            else:
                return a[count:] + a[:count]
        else:
            if in_place:
                for x in xrange(count):
                    a.insert(0, a.pop(-1))
            else:
                return a[-count:] + a[:-count]
    return a

if __name__ == '__main__':
    pass
