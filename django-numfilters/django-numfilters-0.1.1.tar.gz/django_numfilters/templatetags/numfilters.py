import sys
from decimal import Decimal

from django import template

register = template.Library()

req_version = (3,)
cur_version = sys.version_info


def number(value):
    """
    Convert different values to their numbers.
    :param value: a single value.
    :return: single value converted to number.
    :rtype: int or long or float.
    :raises ValueError: if value is not a number.
    """
    if isinstance(value, (int, float, Decimal)):
        return value
    if cur_version < req_version:
        if isinstance(value, long):
            return value
    try:
        return int(value)
    except ValueError:
        return float(value)


def make_safe(func):
    """
    Returns an empty string in any error is raised.
    :param func: a function
    :return: If no exception is raised, `func` result. Otherwise, an empty string.
    """

    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return ''

    return func_wrapper


@make_safe
def absolute_value(obj):
    """
    Return the absolute value of `obj`.
    :param obj: first argument.
    :return: the absolute value of `obj`.
    """
    from operator import abs

    return abs(number(obj))


@register.filter(name='abs')
def abs(obj):
    return absolute_value(obj)


@make_safe
def division(a, b):
    """
    Return `a / b`, for `a` and `b` numbers.
    :param a: first argument.
    :param b: second argument.
    :return: `a / b`
    """
    return number(a) / number(b)


@register.filter(name='div')
def div(a, b):
    return division(a, b)


@make_safe
def exponentiation(a, b):
    """
    Return `a` raised to the power `b`.
    :param a: first argument.
    :param b: second argument.
    :return: `pow(a, b)`
    """
    from operator import pow

    return pow(number(a), number(b))


@register.filter(name='pow')
def pow(a, b):
    return exponentiation(a, b)


@make_safe
def floor_division(a, b):
    """
    Return `a // b`, for `a` and `b` numbers.
    :param a: first argument.
    :param b: second argument.
    :return: `a // b`
    """
    return number(a) // number(b)


@register.filter(name='floordiv')
def floordiv(a, b):
    return floor_division(a, b)


@make_safe
def modulo(a, b):
    """
    Return `a % b`, for `a` and `b` numbers.
    :param a: first argument.
    :param b: second argument.
    :return: `a % b`
    """
    return number(a) % number(b)


@register.filter(name='mod')
def mod(a, b):
    return modulo(a, b)


@make_safe
def multiplication(a, b):
    """
    Return `a * b`, for `a` and `b` numbers.
    :param a: first argument.
    :param b: second argument.
    :return: `a * b`
    """
    return number(a) * number(b)


@register.filter(name='mul')
def mul(a, b):
    return multiplication(a, b)


@make_safe
def square_root(a):
    """
    Return the square root of `a`.
    :param a: first argument.
    :return: `sqrt(a)`
    """
    from math import sqrt

    return sqrt(number(a))


@register.filter(name='sqrt')
def sqrt(a):
    return square_root(a)


@make_safe
def subtraction(a, b):
    """
    Return `a - b`, for `a` and `b` numbers.
    :param a: first argument.
    :param b: second argument.
    :return: `a - b`
    """
    return number(a) - number(b)


@register.filter(name='sub')
def sub(a, b):
    return subtraction(a, b)