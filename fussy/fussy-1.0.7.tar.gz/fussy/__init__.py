"""Provide "embedded firmware" style upgrade mechanics (field upgrades)

"""
try:
    from .version import __version__
except ImportError as err:
    __version__ = '1.0.72'
