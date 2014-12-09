# -*- coding: utf-8 -*-


class fstr(str):
    """String sub-class with a split() method that splits a given indexes.

       Usage::

          >>> r = fstr('D2008022002')
          >>> print r.split(1, 5, 7, 9)
          ['D', '2008', '02', '20', '02']
          >>> _, year, _ = r.split(1,5)
          >>> year
          '2008'
          
    """
    def split(self, *ndxs):
        if len(ndxs) == 0:
            return [self]
        if len(ndxs) == 1:
            i = ndxs[0]
            return [self[:i], self[i:]]

        res = []
        b = 0
        while ndxs:
            a, b, ndxs = b, ndxs[0], ndxs[1:]
            res.append(self[a:b])
        res.append(self[b:])

        return res
