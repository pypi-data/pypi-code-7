# -*- coding: utf-8 -*-

"""Commonly useful decorators.
"""

import time
from django import http
from django.conf import settings


#
# From: http://www.python.org/dev/peps/pep-0318/#examples
#
def attrs(**kwds):
    """Usage::

         @attrs(author='bp@dk.no', created='2009-11-04')
         def myfunc(..):
             ...
    """
    def decorate(f):
        for k in kwds:
            setattr(f, k, kwds[k])
        return f
    return decorate


def require_ndb(fn):
    """Require that a method/fn only runs from the server at ndb (and not
       from www).
    """
    def wrap(request, *args, **kwargs):
        host = request.META.get('HTTP_HOST')
        if host not in ('ndb', 'ndb.datakortet.intern', 'localhost:8000'):
            raise http.Http404
        return fn(request, *args, **kwargs)
    return wrap


def cached(fn):
    """Cache property access
    
       Usage (every access of foo.expensive but the first will use a cached
       value and the database will be hit only once)::
       
          class ...
              @cached
              def expensive(self):
                  return <call expensive db operation here>
              
    """
    def _fn(self):  # properties only take self
        memname = '_' + fn.__name__
        if not hasattr(self, memname):
            setattr(self, memname, fn(self))
        return getattr(self, memname)
    return property(fget=_fn, doc=fn.__doc__)


cached_property = cached


def timecached(secs=10):
    """Cache property access for a certain period of time.
       (useful for long running processes).
    """
    def decorator(fn):
        def _fn(self):
            memname = '_' + fn.__name__
            if not hasattr(self, memname):
                val = fn(self)
                setattr(self, memname, (val, time.time()))
                return val
            else:
                val, t = getattr(self, memname)
                if time.time() - t < secs:
                    return val
                else:
                    val = fn(self)
                    setattr(self, memname, (val, time.time()))
                    return val
            return property(fget=_fn, doc=fn.__doc__)

        return _fn

    return decorator


def redirect_to_host(host, *allowed):
    """Redirect attempts to use a page from the incorrect server.
       (you can pass servers that can handle the page as arguments).
       It allows localhost only in debug mode.
       Note: This will not work with POST requests.
    
       Usage, require ndb (allow also fully qualified ndb)::
    
         @redirect_to_host('ndb', 'ndb.datakortet.intern')
         @login_required
         def view_fn(request, ...):
             ...
    
    """
    if settings.DEBUG:
        allowed += ('localhost:8000',)

    def decorator(fn):
        def wrap(request, *args, **kwargs):
            h = request.META.get('HTTP_HOST')
            if h != host and h not in allowed:

                if request.method() != 'GET':
                    raise SyntaxError(
                        "@redirect_to_host only works with GET requests.")

                goodpath = 'http://' + host + request.path
                return http.HttpResponseRedirect(goodpath)
            
            return fn(request, *args, **kwargs)
        
        return wrap
    
    return decorator
