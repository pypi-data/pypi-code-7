# -*- coding: utf-8 -*-
# Copyright (c) 2014, imageio contributors
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

""" This subpackage provides the core functionality of imageio
(everything but the plugins).
"""

from .util import Image, Dict, asarray, appdata_dir, urlopen  # noqa
from .util import BaseProgressIndicator, StdoutProgressIndicator  # noqa
from .util import string_types, text_type, binary_type, IS_PYPY  # noqa
from .util import get_platform  # noqa
from .findlib import load_lib  # noqa
from .fetching import get_remote_file  # noqa
from .request import Request, read_n_bytes, RETURN_BYTES  # noqa
from .format import Format, FormatManager  # noqa
