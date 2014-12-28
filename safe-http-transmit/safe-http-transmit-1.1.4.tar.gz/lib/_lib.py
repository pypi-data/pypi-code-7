import logging
import urllib.request
import urllib.error
import urllib.parse
import socket
from urllib.parse import urlencode


logger = logging.getLogger(__name__)


class HttpLoadError(RuntimeError):
    pass


class Http404(HttpLoadError):
    pass


class HttpFailedRepeatedly(HttpLoadError):
    pass


def transmit(url, data=None, max_tries=10, timeout=60, error_sleep_time=4, data_dict=None):
    """
    Perform a safe HTTP call, or raise a HttpLoadError.

    The HttpLoadError will probably come in one of it's subclasses,
    Http404 and HttpFailedRepeatedly

    :param url: Example: "http://something.com/"
    :type url: str
    :param data: Data to be posted
    :type data: str
    :param max_tries: How many times should we retry?
    :type max_tries: int
    :param timeout: How long should we wait for each try?
    :type timeout: float
    :param error_sleep_time: How long should we wait before retrying after a failure
    :type error_sleep_time: float
    :param data_dict: Alternative to passing a string for "data"
    :type data_dict: dict
    :return: The body of the HTTP transmission result
    :rtype: bytes
    """
    import time
    logger.debug("Loading {0}".format(url))
    if data_dict:
        if data:
            raise ValueError("Cannot pass data_dict and data")
        data = urlencode(data_dict).encode()
    i = 0
    while True:
        i += 1
        try:
            if timeout is not None:
                rh = urllib.request.urlopen(url, data, timeout=timeout)
            else:
                rh = urllib.request.urlopen(url, data)
            res = rh.read()
            rh.close()
            return res
        except (urllib.error.HTTPError, socket.error, urllib.error.URLError) as e:
            logger.warning("Couldn't load {0}. Got this error: {1}".format(url, e))
            if getattr(e, 'code', '') == 404:
                raise Http404
            if i >= max_tries:
                raise HttpFailedRepeatedly(
                    "Couldn't load {0}. Got this error: {1}".format(url, e))
            time.sleep(error_sleep_time)
