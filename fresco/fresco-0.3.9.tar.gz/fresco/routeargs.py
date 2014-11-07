from operator import attrgetter, itemgetter, methodcaller
from fresco.exceptions import MissingRouteArg
from itertools import cycle

__all__ = ('routearg', 'FormArg', 'PostArg', 'QueryArg', 'GetArg', 'CookieArg',
           'SessionArg', 'RequestObject',
           'FormData', 'PostData', 'QueryData', 'GetData')

_marker = []

magicmethods = [
    '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
    '__complex__', '__contains__', '__del__', '__delattr__', '__delete__',
    '__delitem__', '__delslice__', '__div__', '__divmod__', '__enter__',
    '__eq__', '__exit__', '__float__', '__floordiv__',
    '__ge__', '__getattr__', '__getitem__', '__getslice__',
    '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__', '__idiv__',
    '__ifloordiv__', '__ilshift__', '__imod__', '__imul__', '__index__',
    '__int__', '__invert__', '__iop__', '__ior__', '__ipow__', '__irshift__',
    '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
    '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
    '__neg__', '__nonzero__', '__oct__', '__op__', '__or__', '__pos__',
    '__pow__', '__radd__', '__rand__', '__rcmp__', '__rdiv__', '__rdivmod__',
    '__repr__', '__reversed__', '__rfloordiv__', '__rlshift__', '__rmod__',
    '__rmul__', '__rop__', '__ror__', '__rpow__', '__rrshift__', '__rshift__',
    '__rsub__', '__rtruediv__', '__rxor__', '__setattr__', '__setitem__',
    '__setslice__', '__str__', '__sub__', '__truediv__', '__unicode__',
    '__weakref__', '__xor__']


def map_magics(dest):
    def map_magics(cls):
        dest_method = getattr(cls, dest)
        for item in magicmethods:
            setattr(cls, item, dest_method)
        return cls
    return map_magics


@map_magics('raise_exception')
class LazyException(object):
    """
    A lazy exception uses magic methods to intercept any access to the object
    and raise an exception.
    """

    def __init__(self, exception):
        self.__dict__['_exception'] = exception

    def raise_exception(self, *args, **kwargs):
        raise self.__dict__['_exception']


class RouteArg(object):
    """
    RouteArg objects can be used as keyword arguments in a route definition.
    RouteArgs can extract information from the request and make it available
    to the view.

    For example a RouteArg could be developed that reads information from the
    request cookie::

        Route('/', GET, myview, affiliate=CookieArg('affiliate_id'))

    A naive implementation of ``CookieArg`` could look like this::

        class CookieArg(RouteArg):

            def __init__(self, name):
                self.name = name

            def __call__(self, request):
                try:
                    return request.cookies[self.name].value
                except KeyError,
                    return None

    When the route is constructed the RouteArg's ``configure`` method will
    be called with the Route object and the keyword name.

    At every request, the RouteArg instance will be called and expected to
    supply the value for its argument.
    """

    route = None
    name = None

    def configure(self, route, name):
        self.route = route
        self.name = name

    def __call__(self, request):
        return None


def routearg(func, *args, **kwargs):
    """
    Construct a ``RouteArg`` instance that calls ``func`` with the request
    object as an argument and passes the return value to the routed view.

        def extract_name(req):
            return req.get('name')

        Route('/', GET, myview, name=routearg(extract_name))

    Additional positional and keyword arguments may be passed, eg:

        def name_is(req, *friends):
            return req.get('name') in friends

        Route('/', GET, myview, is_a_friend=routearg(name_is, 'fred', 'jim'))

    """
    class _RouteArg(RouteArg):
        def __call__(self, request):
            return func(request, *args, **kwargs)
    return _RouteArg()


class RequestArg(RouteArg):
    """\
    Extract a view keyword argument from the request object.
    """

    query = attrgetter('query')
    form = attrgetter('form')
    cookies = attrgetter('cookies')
    session = attrgetter('session')

    #: Source for the request variable
    source = form

    #: Exceptions that signal the converter could not do its job due to invalid
    #: input
    converter_exceptions = (ValueError, TypeError)

    def __init__(self, converter=None, key=None,
                 default=_marker, exception=MissingRouteArg):

        self.formkey = key
        self.default = default
        self.required = default is _marker
        self.exception = exception
        self.is_list = isinstance(converter, list)
        if self.is_list:
            self.converter = lambda vs: [c(v)
                                         for c, v in zip(cycle(converter), vs)]
        else:
            self.converter = converter

    def configure(self, route, name):
        if self.formkey is None:
            self.formkey = name
        if self.is_list:
            self.getter = methodcaller('getlist', self.formkey)
        else:
            self.getter = itemgetter(self.formkey)

    def __call__(self, request):
        try:
            value = self.getter(self.source(request))
        except KeyError:
            if self.required:
                return LazyException(
                            self.exception('No value provided for %s' %
                                           (self.formkey,)))
            else:
                return self.default

        try:
            if self.converter is not None:
                value = self.converter(value)
        except self.converter_exceptions:
            value = LazyException(
                        self.exception('%r is not a valid value for %s' %
                                       (value, self.formkey,)))

        return value


class RequestObject(RouteArg):
    """\
    Make the request object itself available as a view argument.

    Example::

        @app.route('/form', POST, request=RequestObject())
        def view(formdata, request):
            ...
    """
    def __call__(self, request):
        return request


class GetData(RouteArg):
    """\
    Make the ``request.form`` MultiDict available as a view argument.

    Example::

        @app.route('/form', POST, data=GetData())
        def view(formdata, data):
            ...
    """

    def __call__(self, request):
        return request.query


#: QueryData may be used as an alias for GetData
QueryData = GetData


class PostData(RouteArg):
    """\
    Make the ``request.form`` MultiDict available as a view argument.

    Example::

        @app.route('/form', POST, data=FormData())
        def view(formdata, data):
            ...
    """

    def __call__(self, request):
        return request.form

#: FormData may be used as an alias for PostData
FormData = PostData


class CookieArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.cookies``.

    Example::

        @app.route('/', GET, message=CookieArg(key='msg', default=None))
        def view(message, message):
            return Response([message])
    """
    source = RequestArg.cookies

    def getter(self, cookies):
        if self.is_list:
            return [c.value for c in cookies.getlist(self.formkey)]
        else:
            return cookies[self.formkey].value

    def configure(self, route, name):
        if self.formkey is None:
            self.formkey = name


class GetArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.query``.

    Example::

        @app.route('/add', GET, a=QueryArg(int), b=QueryArg(int))
        def view(a, b):
            return Response(['a + b = %d' % (a + b)])
    """
    source = RequestArg.query

#: QueryArg may be used as an alias for GetArg
QueryArg = GetArg


class PostArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.form``.

    Example::

        @app.route('/mul', POST, a=FormArg(int), b=FormArg(int))
        def view(a, b):
            return Response(['a * b = %d' % (a * b)])

    """
    source = RequestArg.form

#: FormArg may be used as an alias for PostArg
FormArg = PostArg


class SessionArg(RequestArg):
    """\
    Extract a view keyword argument from ``request.session``.

    Example::

        @app.route('/mul', POST, a=FormArg(int), b=FormArg(int))
        def view(a, b):
            return Response(['a * b = %d' % (a * b)])

    """
    source = RequestArg.session
