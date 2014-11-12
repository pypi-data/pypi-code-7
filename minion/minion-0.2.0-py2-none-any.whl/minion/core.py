from collections import defaultdict

from minion import resource
from minion.request import Manager, Response
from minion.routers import SimpleRouter


class Application(object):
    """
    A Minion application.

    :argument :class:`collections.MutableMapping` config: any app configuration
    :argument :class:`resource.Bin` bin: a resource bin containing resources
        used by views. If unprovided, an empty one will be created (until it is
        populated).
    :argument :class:`request.Manager` manager: a request manager, which
        managers state during each request. If unprovided, one will be created
        and used.
    :argument router: an object satisfying the router interface (see
        :mod:`minion.routers`) to use for route addition and generation for
        this application. If unprovided, a router with simple dictionary lookup
        will be used.
    :argument :class:`jinja2.Environment` jinja: a pre-configured jinja2
        environment, if using jinja2 is desired. (One can be added later, or
        multiple environments used, by calling :meth:`bind_jinja_environment`.)

    """

    def __init__(
        self, config=None, bin=None, manager=None, router=None, jinja=None,
    ):
        if config is None:
            config = {}
        if manager is None:
            manager = Manager()
        if bin is None:
            bin = resource.Bin(manager=manager)
        if router is None:
            router = SimpleRouter()

        self._response_callbacks = defaultdict(list)

        self.bin = bin
        self.config = config
        self.manager = manager
        self.router = router

        self.bind_bin(bin)
        if jinja is not None:
            self.bind_jinja_environment(jinja)

    def route(self, route, **kwargs):
        def _add_route(fn):
            self.router.add_route(route, fn, **kwargs)
            return fn
        return _add_route

    def serve(self, request):
        self.manager.request_started(request)
        view, kwargs = self.router.match(request)

        if view is not None:
            response = view(request=request, **kwargs)
        else:
            response = Response(code=404)

        self.manager.request_served(request, response)
        return response

    def bind_bin(self, bin):
        """
        Bind a resource bin to this application.

        Simply adds the application to the bin globals.

        """

        bin.globals.update([
            ("app", self),
            ("config", self.config),
            ("manager", self.manager),
            ("router", self.router),
        ])

    def bind_jinja_environment(self, environment, resource_name="jinja"):
        """
        Bind useful pieces of the application to the given Jinja2 environment.

        :type environment: :class:`jinja2.Environment`
        :argument str resource_name: the name to bind the environment in the
            application's resource bin. The default is ``'jinja'``.

        """

        self.bin.globals[resource_name] = environment
        environment.globals.update([
            ("app", self),
            ("config", self.config),
            ("router", self.router),
        ])
