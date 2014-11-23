# Copyright (C) 2014 Kieran Colford
#
# This file is part of txt2boil.
#
# txt2boil is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# txt2boil is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with txt2boil.  If not, see <http://www.gnu.org/licenses/>.

"""Transform comments into boilerplate.

This package processes contains all the interfaces for generating
boilerplate for a specific language.  Each language is implemented in
the langs module and is exposed via the toplevel function defined here
called ``language``.

Currently only the following are explicitly supported but the
framework allows for more languages to be added easily.

Supported Languages:
{}

Further support can be added be simply adding classes to the langs
module.

"""

import os
import collections
from . import langs
from . import version


def language(fname, is_ext=False):
    """Return an instance of the language class that fname is suited for.

    Searches through the module langs for the class that matches up
    with fname.  If is_ext is True then fname will be taken to be
    the extension for a language.

    """

    global _langmapping

    # Normalize the fname so that it looks like an extension.
    if is_ext:
        fname = '.' + fname
    _, ext = os.path.splitext(fname)

    return _langmapping[ext]()


_langmapping = collections.defaultdict(langs.Unknown)
_langmapping.update({e.strip(): getattr(langs, nm)
                     for nm in langs.__all__
                     for e in getattr(langs, nm).ext})

__doc__ = __doc__.format('\n'.join(map('- {}'.format, langs.__all__)))
__version__ = version.version
__all__ = ['language']
