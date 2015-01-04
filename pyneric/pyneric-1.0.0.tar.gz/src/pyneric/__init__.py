# -*- coding: utf-8 -*-
"""The `pyneric` package contains Python helpers and utility functions.

For convenience, many of the library's components are imported by the
pyneric package's __init__ module so that they may be accessed directly under
pyneric, such as:

* `~pyneric.fsnotify.FileSystemNotifier`
* `~pyneric.meta.Metaclass`
* `~pyneric.rest_requests.RestResource`
* `~pyneric.util.tryf`

"""

# flake8: noqa

from ._version import __version__, __version_info__
from .fsnotify import *
from .meta import *
from .rest_requests import *
from .util import *
