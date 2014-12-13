import re


def generate_routes(routes_data):
    routes_list = []

    # python 2-3 compatibility
    try:
        routes_data_iteritems = routes_data.iteritems()
    except AttributeError:  # pragma: no cover
        routes_data_iteritems = routes_data.items()

    for name, route_data in routes_data_iteritems:
        route = Route(route_data['path'], route_data['controller'])
        if 'action' in route_data:
            route.set_action(route_data['action'])
        if 'methods' in route_data:
            route.set_methods(route_data['methods'])
        if 'requirements' in route_data:
            route.set_requirements(route_data['requirements'])
        if 'protocols' in route_data:
            route.set_protocols(route_data['protocols'])
        if 'host' in route_data:
            route.set_host(route_data['host'])

        routes_list.append(route)

    return routes_list


class Route:
    # RFC 2616 HTTP request methods
    ALLOWED_METHODS = ('GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'OPTIONS', 'CONNECT', 'PATCH')

    def __init__(self, path, controller, action='action', methods=None, requirements=None, protocols=None, host='.*'):
        """
        @type path: str
        @type controller: str
        @type action: str
        @type methods: tuple
        @type requirements: dict
        @type protocols: tuple
        @type host: str
        """
        if methods:
            methods = self._sanitize_methods(methods)
            self._check_methods(methods)
        else:
            methods = Route.ALLOWED_METHODS

        requirements = self._sanitize_requirements(requirements)

        self.path = self._sanitize_path(path)
        self.controller = controller
        self.action = action
        self.methods = methods
        self.protocols = protocols if protocols else ('http', 'https')
        self.requirements = requirements
        self.host = host

    def set_action(self, action):
        """ @type action: str """
        self.action = action

    def set_methods(self, methods):
        """ @type methods: tuple """
        methods = self._sanitize_methods(methods)
        self._check_methods(methods)
        self.methods = methods

    def set_requirements(self, requirements):
        """ @type requirements: dict """
        self.requirements = self._sanitize_requirements(requirements)

    def set_protocols(self, protocols):
        """ @type protocols: tuple """
        self.protocols = protocols

    def set_host(self, host):
        """ @type host: str """
        self.host = host

    @staticmethod
    def _sanitize_path(path):
        path = path.strip('/')
        if not path:
            path = '/'
        return path

    @staticmethod
    def _sanitize_requirements(requirements):
        """ @type requirements: dict """
        if requirements:
            if not isinstance(requirements, dict):
                raise Exception('Invalid requirements format. They should be a dict')
            for key, value in requirements.items():
                requirements[key] = '(%s)' % value

        else:
            requirements = {}

        return requirements

    @staticmethod
    def _sanitize_methods(methods):
        """ @type methods: tuple """
        return tuple(method.upper() for method in methods)

    def _check_methods(self, methods):
        """ @type methods: tuple """
        for method in methods:
            if method not in self.ALLOWED_METHODS:
                raise Exception('Invalid \'%s\' method' % method)


class Router:
    def __init__(self, routes):
        """ @type routes: tuple or list """
        self.routes = routes

    def match_request(self, request):
        """ @type request: pyhttp.Request """
        for route in self.routes:
            if request.protocol in route.protocols and \
                    (request.method in route.methods or request.method == 'OPTIONS') and \
                    self.have_same_backslashes(route.path, request.path) and \
                    re.compile(route.host).match(request.host):
                mapping = self.find_matches(route.path, request.path, route.requirements)
                if mapping is not None:
                    match = {
                        'controller': route.controller,
                        'action': route.action,
                        'params': mapping
                    }
                    return match
        return False

    @staticmethod
    def have_same_backslashes(one, two):
        """
        @type one: str
        @type two: str
        """
        return len(one.split('/')) == len(two.split('/'))

    @staticmethod
    def find_matches(key_mask, text, requirements=None):
        """
        @type key_mask: str
        @type text: str
        """
        mapping = {}

        expected = key_mask.split('/')
        actual = text.split('/')

        for key, value in zip(expected, actual):
            if len(key) >= 3 and (key[0] == '{' and key[-1] == '}'):
                if not requirements:
                    requirements = {}
                key = key[1:-1]
                if key in requirements and not re.match('^' + requirements[key] + '$', value):
                    return None
                mapping[key] = value
            elif key != value:
                return None

        return mapping
