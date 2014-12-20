# Copyright (c) 2014 by pyramid_decoy authors and contributors
# <see AUTHORS file>
#
# This module is part of pyramid_decoy and is released under
# the MIT License (MIT): http://opensource.org/licenses/MIT
"""pyramid_decoy's views definitions."""

from pyramid.httpexceptions import HTTPFound


def decoy(request):
    """
    Redirect to given page with 302 HTTP status code.

    :param pyramid.request.Request request: pyramid's request.

    :returns: HTTPFound response
    :rtype: pyramid.httpexceptions.HTTPFound
    """
    decoy_url = request.registry['decoy']['url']
    return HTTPFound(location=decoy_url)
