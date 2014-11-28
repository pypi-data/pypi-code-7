from .computation_engine import (apply, join, summarize,
                                 apply_local, join_local, summarize_local,
                                 Engine, output, DelayedException,
                                 fullstream, fullstream_local)

from .fs_cache import CacheBuilder, LocalCacheBuilder

from .std_logger import get_logger

# DO NOT TOUCH THE FOLLOWING LINE:
import sys
if not getattr(sys, "frozen", False):
    import pkg_resources  # part of setuptools
    __version__ = tuple(map(int, pkg_resources.require(__name__)[0].version.split(".")))
else:
    __version__ = (0, 0, 0)
