from _mddb import MemDictStore  # noqa

try:
    from _dsdb import DSStore   # noqa
except ImportError:
    pass

try:
    from _hddb import HDStore   # noqa
except ImportError:
    pass

try:
    from _rtdb import RTStore   # noqa
except ImportError:
    pass
