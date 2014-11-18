import logging
import os


def get_logger(obj=None):

    if obj is not None:
        if hasattr(obj, "__name__"):
            name = "%s.%s" % (obj.__module__, obj.__name__)
        else:
            module = obj.__class__.__module__
            clzname = obj.__class__.__name__
            name = "%s.%s" % (module, clzname)
    else:
        name = ""

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    name = "%-45s" % name
    default_formatter = logging.Formatter("%(asctime)s:%(processName)-14s:" + name + ":%(levelname)s: %(message)s")

    if not(len(logger.handlers)):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(default_formatter)
        logger.addHandler(console_handler)
        file_handler = logging.FileHandler("pacer%d.log" % os.getpid(), "a")
        file_handler.setFormatter(default_formatter)
        logger.addHandler(file_handler)
    return logger
