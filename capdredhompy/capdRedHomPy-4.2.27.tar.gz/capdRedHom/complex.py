from .algorithms import *

class Complex(object):

    def __init__(self, impl):
        self._impl = impl

    @property
    def capd(self):
        return self._impl

    def betti(self):
        return BettiNumbersOverZ(self)()
