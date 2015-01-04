# SegmentTreeNode
# 
# Author : Zhaonan Li.
# Email  : zhaonanproject@gmail.com
# Date   : January, 3rd, 2015


class SegmentTreeNode(object):
    __slots__ = ['start', 'end', 'left', 'right', 'segment_sum']

    def __init__(self, arr, start, end):
        # Input checking.
        if arr is None or len(arr) == 0: raise ValueError('The given array should not be empty.')
        if start > end: raise ValueError('The given start should not be greater than the given end.')
        if not (0 <= start and end <= len(arr) - 1): raise ValueError('The given start and given end is out of the range of arr.')

        self.start = start
        self.end = end
        self.left = None
        self.right = None
        self.segment_sum = 0
        self._add_segment(arr, start, end)


    def query_segment_sum(self, query_start, query_end):
        return self._query_segment_sum(query_start, query_end)


    def update_value(self, index, new_val):
        return self._update_value(index, new_val)


    """ Inner Method. """
    def _add_segment(self, arr, start, end):
        # Base case.
        if start == end:
            self.segment_sum = arr[start]
            return

        mid = (start + end) / 2
        self.left = SegmentTreeNode(arr, start, mid)
        self.right = SegmentTreeNode(arr, mid + 1, end)
        self.segment_sum = self.left.segment_sum + self.right.segment_sum


    def _query_segment_sum(self, query_start, query_end):
        # Base case.
        if query_start <= self.start and self.end <= query_end: return self.segment_sum
        if query_end < self.start or self.end < query_start: return 0

        return self.left.query_segment_sum(query_start, query_end) +\
               self.right.query_segment_sum(query_start, query_end)


    def _update_value(self, index, new_val):
        # Input checking.
        if not (self.start <= index <= self.end): raise ValueError('The given index is out of the range or the current segment node.')
        return self._update_value_helper(index, new_val)


    def _update_value_helper(self, index, new_val):
        # Base case.
        if self.start == self.end == index:
            diff = new_val - self.segment_sum
            self.segment_sum = new_val
            return diff

        mid = (self.start + self.end) / 2
        diff = 0
        if index <= mid:
            diff = self.left.update_value(index, new_val)
        else:
            diff = self.right.update_value(index, new_val)

        self.segment_sum += diff
        return diff

