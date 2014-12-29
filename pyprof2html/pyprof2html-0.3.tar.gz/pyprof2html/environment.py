# -*- coding: utf-8 -*-
"""Global pyprof2html's environment.
"""

from jinja2 import Environment, PackageLoader

__all__ = ['ENVIRON']

CODEC = 'utf-8'
ENVIRON = Environment(loader=PackageLoader('pyprof2html',
                      './templates', encoding=CODEC))
