"""
Logging facilities.
"""

import logging
from .pkginfo import __title__

#: The logging object.
log = logging.getLogger(__title__)

# Add a null handler.
log.addHandler(logging.NullHandler())


def init_logging(verbose=False, formatstring="# %(message)s"):
    # Add a stderr handler.
    handler = logging.StreamHandler()
    log.addHandler(handler)

    fmt = logging.Formatter(formatstring)
    handler.setFormatter(fmt)

    # Set log level.
    log.setLevel(logging.INFO if verbose else logging.WARNING)
