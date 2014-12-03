"""Test django view."""

from django.http import HttpResponse


def bypass(request, *args, **kwargs):
    """View which actually does nothing except return the string representation of the kwargs."""
    if request is not None:
        return HttpResponse(unicode(kwargs))
    return kwargs
