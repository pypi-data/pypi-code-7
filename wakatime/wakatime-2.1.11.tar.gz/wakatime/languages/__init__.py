# -*- coding: utf-8 -*-
"""
    wakatime.languages
    ~~~~~~~~~~~~~~~~~~

    Parse dependencies.

    :copyright: (c) 2013 Alan Hamlett.
    :license: BSD, see LICENSE for more details.
"""


def append_dep(dependencies, item):
    try:
        item = item.split('.')[0]
        if item:
            dependencies.append(item)
    except:
        pass
