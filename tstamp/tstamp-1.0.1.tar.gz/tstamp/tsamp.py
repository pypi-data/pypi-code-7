"""
Author: iLoveTux
Date: 06/04/14
purpose: to provide a class which abstracts away handling of
         current timestamps.

usage:

>>> from timestamp import Timestamp
>>> timestamp = Timestamp()
>>> print timestamp
Wednesday June 04, 17:51:59
>>> print timestamp.epoch
1401918719
>>> print timestamp.timestamp
20140604175159
>>> print timestamp.strftime('%X')
17:51:59
>>> print timestamp.strftime('%x')
06/04/14
>>> print timestamp.strftime('%c')
06/04/14 17:51:59
>>> print timestamp.strftime('%C')

NOTE: timestamp.strftime follows the table here:
    https://docs.python.org/2/library/time.html#time.strftime
"""

from time import time
from datetime import datetime

class Timestamp(object):
    def __init__(self, epoch=None):
        if epoch:
            self._epoch = epoch
        else:
            self._epoch = time()
        self._timestamp = datetime.fromtimestamp(self._epoch)
        self._format = format

    @property
    def epoch(self):
        """
            returns the time (in seconds) since Jan 1, 1970 at midnight.
        """
        return int(self)

    @property
    def friendly(self):
        """
            returns a friendly, human-readable version of the date and time.
        """
        return self._timestamp.strftime('%A %B %d, %X')

    @property
    def timestamp(self):
        """
            returns a pretty useful representation of the time: 
                YYYYmmddhhmmss.
            
            I use this a lot for adding a timestamp to filenames.
        """
        return self._timestamp.strftime('%Y%m%d%H%M%S')

    def strftime(self, format):
        """
            returns the time formatted according to format.
        format follows the rules you can find here:
            https://docs.python.org/2/library/time.html#time.strftime
        """
        return self._timestamp.strftime(format)

    def __repr__(self):
        return str(self._epoch)

    def __str__(self):
        """
            returns a friendly, human-readable version of the date and time.
        """
        return self.friendly

    def __int__(self):
        """
            returns the time (in seconds) since Jan 1, 1970 at midnight.
        """
        return int(self._epoch)
