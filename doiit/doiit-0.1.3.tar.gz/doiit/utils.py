# -*- coding: utf-8 -*-

import math


def cut_list(l, per_page):
    for i in range(int(math.ceil(len(l)/100.0))):
        yield l[i * 100: (i+1) * 100]
