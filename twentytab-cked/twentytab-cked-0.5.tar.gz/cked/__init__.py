VERSION = (0, 5)
__version__ = '.'.join(map(str, VERSION))
DATE = "2014-12-12"
try:
    from . import conf
except:
    pass