import logging
import collections

FORMAT = "+++ %(asctime)s - %(name)s.%(funcName)s - %(message)s"
logging.basicConfig(filename='/dev/null', level=logging.INFO)

#logging.disable(logging.INFO)

def get_logger(obj, form=FORMAT):
    if type(obj) == str:
        key = obj
    else:
        key = '%s.%s' % (obj.__class__.__module__, obj.__class__.__name__)
    logger = logging.getLogger(key)
    logger.setLevel(logging.DEBUG)

    # Console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter(form))
    logger.addHandler(ch)

    return logger

