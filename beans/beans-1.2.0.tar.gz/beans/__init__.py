"""

The Beans Python Business Library

This module provides a wrapper around the Beans Business API, the
interface to the api is provided by the :py:class:`beans.Business`
object.

Copyright 2014 Beans
"""

__version__ = '1.2.0'

from .exception import BeansException

from .api import Beans

default = None
get = None
post = None
delete = None
get_token_from_cookie = None


def init(secret=None, logger=None, fail_silently=True, signature='My Python App v0'):
    global default, get, post, delete, get_token_from_cookie
    default = Beans(secret, logger=logger, fail_silently=fail_silently, signature=signature)
    default.version = __version__
    get = default.get
    post = default.post
    delete = default.delete
    get_token_from_cookie = default.get_token_from_cookie