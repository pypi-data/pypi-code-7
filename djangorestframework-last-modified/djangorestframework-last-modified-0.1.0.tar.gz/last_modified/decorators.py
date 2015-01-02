import logging
from functools import wraps
from calendar import timegm

from django.utils.decorators import available_attrs
from rest_framework import status
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from django.utils.http import http_date, parse_http_date_safe
from django.utils import six

logger = logging.getLogger('django.request')


def prepare_header_name(name):
    """Copied from https://github.com/chibisov/drf-extensions/blob/master/rest_framework_extensions/utils.py

         >> prepare_header_name('Accept-Language')
         http_accept_language
     """
    return 'http_{0}'.format(name.strip().replace('-', '_')).upper()


class LastModifiedProcessor(object):
    """Based on https://github.com/django/django/blob/master/django/views/decorators/http.py
       and on https://github.com/chibisov/drf-extensions/blob/master/rest_framework_extensions/etag/decorators.py"""

    def __init__(self, last_modified_func=None):
        self.last_modified_func = last_modified_func

    def __call__(self, func):
        this = self

        @wraps(func, assigned=available_attrs(func))
        def inner(self, request, *args, **kwargs):
            return this.process_conditional_request(
                view_instance=self,
                view_method=func,
                request=request,
                args=args,
                kwargs=kwargs,
            )

        return inner

    def process_conditional_request(self,
                                    view_instance,
                                    view_method,
                                    request,
                                    args,
                                    kwargs):
        if_modified_since = self.get_if_modified_since(request)
        res_last_modified = self.calculate_last_modified(
            view_instance=view_instance,
            view_method=view_method,
            request=request,
            args=args,
            kwargs=kwargs,
        )

        if request.method in SAFE_METHODS and self.is_hasnt_been_modified(res_last_modified, if_modified_since):
            response = Response(status=status.HTTP_304_NOT_MODIFIED)
        else:
            response = view_method(view_instance, request, *args, **kwargs)

        if res_last_modified and not response.has_header('Last-Modified'):
            response['Last-Modified'] = http_date(res_last_modified)

        return response

    def get_if_modified_since(self, request):
        if_modified_since = request.META.get(prepare_header_name("if-modified-since"))
        if if_modified_since:
            if_modified_since = parse_http_date_safe(if_modified_since)
        return if_modified_since

    def calculate_last_modified(self,
                                view_instance,
                                view_method,
                                request,
                                args,
                                kwargs):
        if isinstance(self.last_modified_func, six.string_types):
            last_modified_func = getattr(view_instance, self.last_modified_func)
        else:
            last_modified_func = self.last_modified_func
        if last_modified_func:
            dt = last_modified_func(
                view_instance=view_instance,
                view_method=view_method,
                request=request,
                args=args,
                kwargs=kwargs,
            )
            if dt:
                res_last_modified = timegm(dt.utctimetuple())
            else:
                res_last_modified = None
        else:
            res_last_modified = None

        return res_last_modified

    def is_hasnt_been_modified(self, res_last_modified, if_modified_since):
        return res_last_modified and if_modified_since and res_last_modified <= if_modified_since


last_modified = LastModifiedProcessor
