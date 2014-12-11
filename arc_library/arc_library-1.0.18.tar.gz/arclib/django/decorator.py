#-*- coding: utf-8 -*-
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

def api(func):
    @csrf_exempt
    @require_http_methods(["POST"])
    def wrap(request, *args, **kwargs):
        return func(request, *args, **kwargs)

    wrap.__doc__ = func.__doc__
    wrap.__name__ = func.__name__
    return wrap