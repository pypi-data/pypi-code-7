import re
import collections

from . import interface


Entry = collections.namedtuple('Entry', 'regex method handler'
                                        ' check_cors cors_options')


class _CORSCheckMixin:
    pass


class URLDispatch(interface.AbstractResolver, _CORSCheckMixin):
    """Resolver using url dispatching."""

    DYN = re.compile(r'^\{[_a-zA-Z][_a-zA-Z0-9]*\}$')
    GOOD = r'[^{}/]+'
    PLAIN = re.compile('^'+GOOD+'$')

    METHODS = {'POST', 'GET', 'PUT', 'DELETE', 'PATCH', 'HEAD'}

    def __init__(self):
        self._urls = []

    def add_url(self, method, path, handler, *, name=None):
        """Registers handler for URL pattern.

        method -- request method (eg: GET/POST/PUT/DELETE)
        path -- uri path pattern
        handler -- callback which will be called (yielded from)
                   with single argument `request`.
        name -- optional name for this method+path pattern
        """
        assert callable(handler), handler
        assert path.startswith('/'), path
        method = method.upper()
        assert method in self.METHODS, method
        regexp = []
        for part in path.split('/'):
            if not part:
                continue
            if self.DYN.match(part):
                regexp.append('(?P<'+part[1:-1]+'>'+self.GOOD+')')
            elif self.PLAIN.match(part):
                regexp.append(part)
            else:
                raise ValueError("Invalid path '{}'['{}']".format(path, part))
        pattern = '/' + '/'.join(regexp)
        if path.endswith('/') and pattern != '/':
            pattern += '/'
        try:
            compiled = re.compile('^' + pattern + '$')
        except re.error:
            raise ValueError("Invalid path '{}'".format(path))
        # cors_options = collections.ChainMap(cors_options, self.CORS_OPTIONS)
        # allow_origin = cors_options.get('allow-origin')
        # if allow_origin is not None:
        #     assert callable(allow_origin) \
        #         or isinstance(allow_origin, (collections.Sequence, str)), \
        #         "Invalid 'allow-origin' option {!r}".format(allow_origin)
        self._urls.append(Entry(compiled, method, handler, '', ''))
        #                        check_cors, cors_options))

    def url_for(self, name, **params):
        pass

    def resolve(self, request):
        pass
