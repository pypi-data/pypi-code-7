
# python standard library
from bisect import insort

# third party
import numpy


class SortedList(list):
    """
    Extends the `list` built-in with `insort`
    """
    def __init__(self, *args, **kwargs):
        """
        Sorted List Constructor 
        """
        super(SortedList, self).__init__(*args, **kwargs)
        return

    
    def insort(self, item):
        """
        Inserts item into list in sorted order
        """
        insort(self, item)
        return

    def percentile(self, percentile):
        """
        Calculates the percentile for the current list.

        :param:

         - `percentile`: number in range [0,100] (e.g. 50 gets median)

        :return: value for percentile
        """
        return numpy.percentile(self, percentile)
