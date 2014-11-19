"""
Docstring for the ``subjects`` module.
"""

class Person(object):
    """A person to be indoctrinated."""

    def __init__(self, name):
        """Build a new MyClass.

        Args:
            name (str): What the person likes to be called.
        """
        self.name = name

    def say_hello(self):
        """Greet the Person, warmly."""
        print "Hello, %s" % self.name
