#    -*- coding: utf-8 -*-

from __future__ import print_function

from types import TupleType, ListType

__author__ = 'francis'
__version__ = '0.0.1'
__url__ = 'https://bitbucket.org/sys-git/spirol'
__email__ = 'francis.horsman@gmail.com'
__short_description__ = 'A pure-python clockwise non-repeating outside-in spiral iterator-generator for 2D arrays'

class InputFormatError(Exception):
    """
    The input array over which the spirol is iterating is not a pure two dimensional array.
        ie: the number of elements in the input array is not equal to the sum of the array dimensions.
    """
    pass


class spirol(object):
    """
    A generator iterator that takes a two dimensional iterator as input and outputs
    items from the iterator in a clockwise circular non-repeating shrinking spiral
    until the input iterator is exhausted.
    """
    NUM_MAX_ITEMS_TO_PRINT = 10

    def __init__(self, array, size, verbose=False, debug=False, print_max_items=NUM_MAX_ITEMS_TO_PRINT):
        """

        :type array: two-dimensional iterable containing the required data.
        :type size: tuple (num_rows, num_cols) in the array.
        :type verbose: bool True: output debugging info, False - otherwise.
        :param debug: bool False - yield as iterator, True: otherwise.
        :attention: No validity is done on the input array because it is assumed that the input array is an iterable
            (which may be a generator - and we want to use generators if at all possible to save memory given that the
            input array may be unbounded.
        :return:
        """
        if not isinstance(size, (TupleType, ListType)):
            raise ValueError('size must be a tuple(num_rows, num_cols)')
        self._size = {'rows': size[0], 'cols': size[1]}
        self._array = array
        self._verbose = bool(verbose)
        self._debug = bool(debug)
        self._print_max_items = int(print_max_items) if print_max_items else spirol.NUM_MAX_ITEMS_TO_PRINT

    def __iter__(self):
        col_start = row_start = row = 0
        if self._debug: result = []

        cols = self._size['cols']
        rows = self._size['rows']

        try:
            while True:
                #   Can we go right?
                if not (cols-col_start) > 0:
                    self._verbose and print('Cannot go right')
                    break
                else:
                    for col in xrange(col_start, cols):
                        if self._debug:
                            result.append((row, col))
                        else:
                            yield self._array[row][col]

                #   Can we go down?
                if not (rows-(row_start+1)) > 0:
                    self._verbose and print('Cannot go down')
                    break
                else:
                    for row in xrange(row_start+1, rows):
                        if self._debug:
                            result.append((row, col))
                        else:
                            yield self._array[row][col]

                #   Can we go left?
                if not ((col - 1)-(col_start-1)) > 0:
                    self._verbose and print('Cannot go left')
                    break
                else:
                    for col in xrange(col-1, col_start-1, -1):
                        if self._debug:
                            result.append((row, col))
                        else:
                            yield self._array[row][col]

                #   Can we go up?
                if not ((row - 1)-row_start) > 0:
                    self._verbose and print('Cannot go up')
                    break
                else:
                    for row in xrange(row-1, row_start, -1):
                        if self._debug:
                            result.append((row, col))
                        else:
                            yield self._array[row][col]

                row_start += 1
                col_start += 1
                cols -= 1
                rows -= 1
                if self._debug:
                    self._verbose and print(result)
            if self._debug:
                self._verbose and print(result)
            else:
                raise StopIteration()
        except IndexError as e:
            raise InputFormatError(e)

    def __repr__(self):
        return 'spirol(%s, %s)' % (self._size['rows'], self._size['cols'])

    def __unicode__(self):
        return str(self)

    def __str__(self):
        def max_items(l=self._print_max_items):
            items = [i for i in iter(self)]
            l = min(l, len(items))
            if len(items) > l:
                a = ', '.join([str(i) for i in items[:l/2]])
                b = ', '.join([str(i) for i in items[len(items)-l/2:]])
                return ''.join(['[', '...'.join([a, b]), ']'])
            else:
                return ', '.join(['%s' % items])
        return ': '.join([self.__repr__(), max_items()])

    def __len__(self):
        return len([i for i in iter(self)])

if __name__ == '__main__':
    pass
