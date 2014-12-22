
# python standard library
import time

# this package
from ape import BaseClass
from ape import CREATION, ARGS, KWARGS
from ape import CALLED_ON, CALLED, NOT_IMPLEMENTED

# this module
from callclass import CallClass


output_documentation = __name__ == '__builtin__'


class DummyClass(BaseClass):
    """
    The Dummy Class does nothing
    """
    def __init__(self, *args, **kwargs):
        """
        Dummy class constructor
        """
        super(DummyClass, self).__init__()
        self._logger = None
        self.logger.info(CREATION.format(thing=self))
        self.logger.info(ARGS.format(value=args))
        self.logger.info(KWARGS.format(value=kwargs))
        for name, value in kwargs.items():
            setattr(self, name, value)
        return

    def __call__(self, *args, **kwargs):
        """
        Logs the fact that it was called
        """
        self.logger.info(CALLED.format(thing=self))
        self.logger.info(ARGS.format(value=args))
        self.logger.info(KWARGS.format(value=kwargs))
        return

    def __str__(self):
        """
        Returns the class name
        """
        return self.__class__.__name__

    def __getattr__(self, attribute):
        """
        To catch unimplemented parts of the class and log them
        """
        self.logger.info(CALLED_ON.format(attribute=attribute,
                                          thing=self))
        return CallClass(NOT_IMPLEMENTED.format(thing=self))
# end class Dummy    


class CrashDummy(DummyClass):
    """
    A dummy that crashes
    """
    INIT = '__init__'
    CALL = '__call__'
    CHECK_REP = 'check_rep'
    CLOSE = 'close'
    def __init__(self, error, error_message="CrashDummy is crashing.",
                 function=CALL,
                 *args, **kwargs):
        """
        CrashTestDummy Constructor

        :param:

         - `error`: an exception (object) to raise
         - `error_message`: string to pass to error on raising
         - `function`: which function to raise error (__call__, check_rep, close, __init__)
        """
        super(CrashDummy, self).__init__(*args, **kwargs)
        self.error = error
        self.error_message = error_message
        self.function = function
        if function == self.INIT:
            raise error(error_message)
        return

    def check_rep(self):
        """
        crashes on check_rep() if that's the function
        """
        if self.function == self.CHECK_REP:
            raise self.error(self.error_message)
        return

    def close(self):
        """
        Crashes if close is the function
        """
        if self.function == self.CLOSE:
            raise self.error(self.error_message)
        return

    def __call__(self):
        """
        Raises error if self.function is __call__ (this needs to be defined to work)
        """
        if self.function == self.CALL:
            raise self.error(self.error_message)
        return 

    def __getattr__(self, attribute):
        """
        To catch unimplemented parts of the class and log them

        :param:

         - `attribute`: string for attribute not defined elsewhere in the class

        :raise: self.error if attribute == self.function
        """
        self.logger.info(CALLED_ON.format(attribute=attribute,
                                          thing=self))        
        if attribute == self.function:
            raise self.error(self.error_message)
        return CallClass(NOT_IMPLEMENTED.format(thing=self))

# end class CrashDummy        


class HangingDummy(DummyClass):
    """
    A dummy that hangs
    """
    def __init__(self, *args, **kwargs):
        super(HangingDummy, self).__init__(*args, **kwargs)
        return

    def __call__(self, *args, **kwargs):
        """
        Sleeps for three years in an infinite loop
        """
        super(HangingDummy, self).__call__(*args, **kwargs)
        while True:
            time.sleep(10**7)
        return
# end class HangingDummy


# python standard library
import unittest

# third-party
try:
    from mock import MagicMock
except ImportError:
    pass    


class TestCrashDummy(unittest.TestCase):
    def setUp(self):
        self.dummy = CrashDummy(error=RuntimeError, other='other')
        self.dummy._logger = MagicMock()
        return

    def test_crash(self):
        self.assertRaises(RuntimeError, self.dummy)


if output_documentation:
    class FakeLogger(object):
        def info(self, output):
            print output
            
    class KingKong(DummyClass):
        def __init__(self, *args, **kwargs):
            super(KingKong, self).__init__(*args, **kwargs)
            self._logger = FakeLogger()
            return
    

    kongs = (KingKong(index, name) for index,name in enumerate('Kong MightyJoe'.split()))
    for kong in kongs:
        kong.rampage()
        kong('fay wray')


if __name__ == '__main__':
    class FakeLogger(object):
        def info(self, output):
            print output
            
    class KingKong(DummyClass):
        def __init__(self, *args, **kwargs):
            super(KingKong, self).__init__(*args, **kwargs)
            self._logger = FakeLogger()
            return    

    kongs = (KingKong(index, name) for index,name in enumerate('Kong MightyJoe'.split()))
    for kong in kongs:
        kong.rampage()
        kong('fay wray')
