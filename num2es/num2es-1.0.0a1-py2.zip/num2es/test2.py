#!/usr/bin/env python
# -*- coding: utf-8 -*-

from num2es import TextNumber

n = TextNumber(31115432877)
print(n.number)
print(n.nice_repr())
print(unicode(n))