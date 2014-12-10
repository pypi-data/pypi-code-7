"""Base version classes."""
import re
from distutils.version import LooseVersion, StrictVersion


class Version(object):
    """
    A verifieable, comparable version. A version is expected to a semantic version of the form
    ``vA.B.C`` where A, B, and C are the major number, minor number, and patch number respectivley.
    Shorter version strings are allowed as well as various version suffixes. Under the hood this
    value is stripped of the leading 'v' and passed to distutils' ``StrictVersion`` for purposes of
    comparison. Other forms are possible but patterns accepted by ``StrictVersion`` are compared
    before other patterns.

    The following two rules define comparisons:
    - Verified greater than unverified.
    - Strict greater than loose.
    - Strict versions compared directly using ``StrictVersion``.
    - Everything else compared directly using ``LooseVersion``.
    """
    _strict_re = (r'^v([0-9])', '\\1')

    def __init__(self, value, verified):
        """Initialize the version value."""
        self.value = value
        self.verified = verified

    def __str__(self):
        return self.value

    def __repr__(self):
        return 'Version<{}, {}>'.format(repr(self.value), repr(self.verified))

    def loose(self):
        """Return the version's ``LooseVersion``."""
        return LooseVersion(self.value)

    def strict(self):
        """Return the version's ``StrictVersion`` or ``None`` if not strict."""
        pattern = re.compile(self._strict_re[0])
        if pattern.match(self.value):
            version = pattern.sub(self._strict_re[1], self.value)
            try:
                return StrictVersion(version)
            except ValueError:
                pass
        return None

    def _validate_comparison(self, obj):
        """Raise a ``TypeError`` if obj may not be compared to self."""
        if (not hasattr(self, 'loose') or not hasattr(self, 'strict') or
                not hasattr(self, 'verified')):
            raise TypeError("cannot compare {} with {}".format(
                self.__class__.__name__, obj.__class__.__name__))

    def __le__(self, obj):
        """Return True if obj is less than or equal to self."""
        self._validate_comparison(obj)
        if self.verified != obj.verified:
            return bool(obj.verified)

        s1, s2 = self.strict(), obj.strict()
        if s1 is None and s2 is None:
            return self.loose() <= obj.loose()
        elif s1 is None:
            return True
        elif s2 is None:
            return False
        return s1 <= s2

    def __lt__(self, obj):
        """Return True if self is less than obj."""
        self._validate_comparison(obj)
        if self.verified != obj.verified:
            return bool(obj.verified)

        s1, s2 = self.strict(), obj.strict()
        if s1 is None and s2 is None:
            return self.loose() < obj.loose()
        elif s1 is None:
            return True
        elif s2 is None:
            return False
        return s1 < s2

    def __eq__(self, obj):
        """Return True if self is equal to obj."""
        self._validate_comparison(obj)
        return self.value == obj.value and self.verified == obj.verified

    def __ne__(self, obj):
        """Return True if self is not equal to obj."""
        return not self.__eq__(obj)

    def __ge__(self, obj):
        """Return True if self is greater than or equal to obj."""
        return not self.__lt__(obj)

    def __gt__(self, obj):
        """Return True if self is greater than obj."""
        return not self.__le__(obj)


class Detector(object):
    """Base version detector. May be interated upon."""

    def __init__(self, container):
        """Initialize the versions object for a particular container."""
        self.container = container

    def __iter__(self):
        """Return an iterator over the detected versions."""
        return self.detect().__iter__()

    def detect(self):
        """Return a generator which yields the container versions."""
        raise NotImplemented()
