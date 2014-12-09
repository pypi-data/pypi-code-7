# -*- coding: utf-8 -*-

"""pset subclass that works as a django template context.
"""

# pylint:disable=R0903
# R0903: too few public methods.

import weakref
import uuid
import pickle
import urllib

from django.conf import settings
from django.template import context
from dk.utils import u8
from dk.dklogger import dklogger


logger = dklogger(__name__, debug=False, info=False)

from .pset import pset


class Forms(pset):
    """A descriptor that makes a page (below) and its forms, mutually
       'self'-aware.  Needed by the forms templates to manage the csrf
       token.
    """
    def __get__(self, pageclass, owner):
        if pageclass is None:
            raise AttributeError('forms is an instance...')
        self.page = pageclass  # pylint:disable=W0201
        return self

    def __iter__(self):
        return iter(self.values())


class _deferred(object):
    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args

    def __call__(self):
        return self.fn(*self.args)
    

class pageproperty(object):
    """`@property`-like decorator for properties on sub-classes of page.
    """
    def __init__(self, get):
        self.get = get
        if hasattr(get, '__doc__'):
            self.__doc__ = get.__doc__

    def __get__(self, pageobj, pageclass=None):
        if pageobj is None:
            return self
        return self.get(pageobj)


class deferred(object):
    """Decorator that doesn't evaluate the property until template evaluation
       and in such a way that the property is only evaluated once for each
       mention in the template.
       Not suitable for use in view code.
    """
    def __init__(self, get):
        #logger.debug("DEFERRED::init", get.__name__, dir(get))
        self.get = get
        if hasattr(get, '__doc__'):
            self.__doc__ = get.__doc__

    def __get__(self, pageobj, pageclass=None):
        if pageobj is None:
            return self
        return _deferred(self.get, pageobj)


class cached(object):
    """Decorator that creates a property who's method is only evaluated
       once. Great for properties that would otherwise hit the database
       at declaration time.

       Obviously not suitable for dynamic properties (properties who's
       values change during the life time of a view).
    """
    def __init__(self, get):
        #print "CACHED", get.__name__, dir(get)
        #logger.debug("cached init", get.__name__, dir(get))
        self.get = get
        if hasattr(get, '__doc__'):
            self.__doc__ = get.__doc__

    def __get__(self, pageobj, pageclass=None):
        #print "CACHED/get", self.get.__name__
        if pageobj is None:
            return self
        if not hasattr(self, '_value'):
            self._value = self.get(pageobj)
        return self._value

    def __set__(self, obj, val):
        #print 'setting...'
        self._value = val
        return self
        

class page(pset):
    """The ``page`` class is used as a container for variables a view
       function wants to pass on to the template.  Idiomatic usage::

           def myview(request, ...):
               page = adt.page(request)
               ...
               return dkhttp.render_to_response('template.html', page)

        when django renders a template variable it first calls

            page.__contains__(variable)

        and if that returns true it calls

            page.__getitem__(variable)

        (if that doesn't suceed it will continue..)

        page must not be completely empty.

    """
    forms = Forms()  # all the forms on the page
    
    def __init__(self, request, grab=()):
        super(page, self).__init__()
        
        # If path is funky (i.e. it contains GET parameters that aren't
        # ascii), then we ought to redirect to self.full_path.
        # Otherwise the GET variables will contain \ufffd characters.
        # FF and IE do this in subtly different ways, so test thoroughly
        # if changing any of this :-)
        # Note: normally we would never have GET parameters that we don't
        #       control, so this is hardly ever a real problem...
        rmqs = request.META.get('QUERY_STRING')
        querystring = urllib.unquote(rmqs or '')
        qquery = urllib.quote(u8(querystring), '=&')

        fullpath = u8(request.path)
        funky = False
        if querystring:
            funky = querystring != u8(querystring)
            fullpath += '?' + qquery
        
        for v in grab:
            self[v] = request.REQUEST.get(v)

        # set a number of common variables in the environment.
        # use dictionary syntax to prevent infinite recursion in
        # __setattr__
        #self['user'] = getattr(request, 'user', None)
        self['path'] = u8(request.path)   # hmm.. u8?
        self['full_path'] = fullpath
        self['funky_path'] = funky
        self['session'] = request.session
        self['method'] = request.method
        self['COOKIES'] = request.COOKIES
        self['LANGUAGE_CODE'] = getattr(request, 'LANGUAGE_CODE', None)
        self['DEBUG'] = settings.DEBUG
        
        self['is_post'] = self['method'] == 'POST'
        self['is_get'] = self['method'] == 'GET'
        self['request'] = request
        ip = request.META.get('REMOTE_ADDR')
        self['adminip'] = ip in settings.INTERNAL_IPS
        self['page_secret_selfref'] = weakref.proxy(self)  # don't create cycle
        self['uuid'] = str(uuid.uuid1())
        self._predefined = []

        for processor in context.get_standard_processors():
            self.update(processor(request))

        self.mark()
        #self._predefined = self._order[:]  # shallow copy of known names

    #@cached
    def user(self):
        "Hits the User table."
        #print "USER:"
        return getattr(self.request, 'user', None)

    def __getattr__(self, key):
        return super(page, self).__getattr__(key)

    def __setattr__(self, key, val):
        if key.startswith('_'):
            object.__setattr__(self, key, val)
        else:
            if self._ownsattr(key):
                object.__setattr__(self, key, val)

            if getattr(val, 'is_form', False):
                self.forms[key] = val
            self._add(key, val)

    def _ownsattr(self, attr):
        """When called from a subclass, this returns true iff the `attr` is
           defined on the subclass (ie. is not a method defined on
           :class:`core.adt.page`.
        """
        return hasattr(self, attr) and not hasattr(super(page, self), attr)

    def __contains__(self, key):
        return super(page, self).__contains__(key) or self._ownsattr(key)

    def __getitem__(self, key):
        if self._ownsattr(key):
            return getattr(self, key)
        elif super(page, self).__contains__(key):
            return super(page, self).__getitem__(key)
        else:
            raise KeyError("Unknown key: %r" % key)

    def mark(self, persist=False):
        "Mark currently known item keys."
        if persist:
            self._predefined = self._order[:]  # shallow copy of known names
        return self._order[:]

    def viewstate(self, mark=None):
        """Return viewstate from ``mark``.
           Viewstate ::= variables/values that have been defined on page.
        """
        state = {}
        skiplist = set(mark or self._predefined)

        def can_pickle(var, val):
            "Is the variable/value picleable?"
            
            if var in ('request', 'session', 'page_secret_selfref', 'dkhttp'):
                return False

            if var == 'messages' and 'FallbackStorage' in str(type(val)):
                return False
            
            if not hasattr(val, '__dict__'):
                # all basic types (int, str, etc.) are pickleable
                return True

            if hasattr(val, '__getstate__'):
                logger.debug('%s [%s] has __getstate__' % (var, type(val)))
                return True

            # pylint:disable=W0212
            if hasattr(val, '_can_pickle'):
                logger.debug('%s._can_pickle = %r' % (var, val._can_pickle))
                return val._can_pickle
            
            try:
                pickleable = val == pickle.loads(pickle.dumps(val))
                logger.debug(
                    'checking %s [%s]: %r' % (var, type(val), pickleable))
                
                if not pickleable:
                    logger.error(
                        ' '.join("""
                           Variable [%s] of type [%s] doesn't raise a
                           TypeError when pickled, but the value is
                           not __eq__ to the roundtripped value.
                        """.split()) % (var, type(val)))
                    
                return pickleable
            
            except TypeError:
                # only issue warning if we had to manually test picleability.
                msg = ' '.join("""
                    Variable [%s] of type [%s] is not pickleable.
                    You can remove this warning by setting the attribute
                    _can_pickle to False on the object.
                    """.split())
                logger.warning(msg % (var, type(val)), exc_info=1)
                return False
            
        for var in self._order:
            if var not in skiplist:
                val = self[var]

                if can_pickle(var, val):
                    state[var] = val
                else:
                    logger.info(' '.join(
                        """Variable %s [%s] will not be part of the
                           viewstate because it can't be pickled.
                           Turn loglevel to logging.DEBUG to see why.
                           """.split()) % (var, type(val)))
                
        return state

    def fetch_view_vars(self):
        """WARNING: security risk!
        
           Return a list of pset(name, value) objects for all
           properties added after ``__init__``.  This will typically
           be the variables the view has added (hence the name).

           This function is useful when the template needs to capture its
           (the view's) context and pass it on in an ajax call.

           You can get at it from a template tag::

               page = template.Variable('page').resolve(ctx)
               ctx['view_vars'] = page.fetch_view_vars()
               
        """
        res = []
        for var in self._order:
            if var not in self._predefined:
                val = self[var]
                if hasattr(val, '__dict__'):
                    if hasattr(val, '__json__'):
                        res.append(pset(name=var, value=val.__json__()))
                    else:
                        pass  # general case is not safe.
                else:
                    res.append(pset(name=var, value=val))
        return res
