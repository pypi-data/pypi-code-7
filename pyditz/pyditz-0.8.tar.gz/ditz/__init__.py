"""
Python implementation of Ditz (http://ditz.rubyforge.org).
"""

import pkg_resources as pkg

from .plugin import loader

path = pkg.resource_filename(__name__, "plugins")
loader.add_path(path)

del path, loader, pkg
