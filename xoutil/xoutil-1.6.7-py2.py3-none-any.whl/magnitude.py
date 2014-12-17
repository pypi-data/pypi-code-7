
from xoutil.objects import metaclass


class MagnitudeType(type):
    pass


class MagnitudeBase(metaclass(MagnitudeType), type):
    def __mul__(self, other):
        pass


class _val(metaclass(MagnitudeBase), object):
    def __init__(self, val):
        self.val = val

    def __mul__(self, other):
        from numbers import Number
        if isinstance(other, Number):
            return type(self)(self.val * other)
        else:
            return (type(self)*type(other))(self.val * other.val)
    __rmul__ = __mul__

    def __div__(self, other):
        from numbers import Number
        if isinstance(other, Number):
            return type(self)(self.val / other)
        else:
            return (type(self)*type(other))(self.val / other.val)

    def __add__(self, other):
        if isinstance(other, type(self)):
            return type(self)(self.val + other.val)
        else:
            raise TypeError()
    __radd__ = __add__


# EUR + EUR, ok
# EUR + USD = EUR + (ct * EUR/USD) * USD  assumed a rate

# Km + m = 1000 * m + m, ok
# Km + Km, ok
# Km * Km, ok (Km^2)
# Pax * Night, ok


# $/(Pax * Night), etc...


# ct * _some_uom_, ok


class Space(MagnitudeBase):
    m = 1   # the basic unit.
    km = 1000*m
    cm = m/100
    mm = m/1000

km = Space.km
meter = Space.m

assert km == 1000 * meter


class Time(MagnitudeBase):
    s = sec = 1
    min = 60 * sec
    hr = 60 * min
    ms = s/1000
second = Time.s
hour = Time.hr

assert hour = 3600 * second

Velocity = Space/Time
assert Velocity.unit == meter/second


Acceleration = Velocity/Time
assert Acceleration.unit == meter/(second**2)

g = 9.8 * Acceleration.unit


assert Acceleration * Time == Velocity


class Unit(MagnitudeBase):
    u = 1


class Consumption(MagnitudeBase):
    night = 1


class Money(MagnitudeBase):
    peso = 1


PriceUnit = Money/(Unit * Consumption)

PriceTotal = Unit * Consumption * PriceUnit
