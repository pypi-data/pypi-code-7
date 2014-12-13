import sys
from pyrouter.router import Router


class DispatcherException(Exception):
    pass


class Dispatcher:
    def __init__(self, routes, not_found_handler, dependencies=None):
        """
        @type routes: list or tuple
        @type not_found_handler: apy.handler.ErrorHandler
        @type dependencies: dict, list, tuple
        """
        self._routes = routes
        self._not_found_handler = not_found_handler
        if dependencies is None:
            dependencies = {}
        self._dependencies = dependencies

        if not isinstance(self._dependencies, (list, tuple, dict)):
            raise DispatcherException('Invalid dependencies type')

    def _load_controller(self, module_class, request):
        """ @type request: apy.http.Request """
        module_name, class_name = module_class.rsplit('.', 1)
        __import__(module_name)
        module = sys.modules[module_name]
        if isinstance(self._dependencies, (list, tuple)):
            controller_object = getattr(module, class_name)(request, *self._dependencies)
        else:
            controller_object = getattr(module, class_name)(request, **self._dependencies)
        return controller_object

    @staticmethod
    def _run_controller_method(controller, action_name, params=None):
        response = getattr(controller, action_name, lambda: None)(**params)
        return response

    def dispatch(self, request):
        """ @type request: apy.http.Request """
        router = Router(self._routes)
        result = router.match_request(request)

        if not result:
            if isinstance(self._dependencies, (list, tuple)):
                return self._not_found_handler(request, *self._dependencies)
            else:
                return self._not_found_handler(request, **self._dependencies)

        module_class = result['controller']
        controller = self._load_controller(module_class, request)
        params = result['params']
        action_name = result['action']

        response = self._run_controller_method(controller, action_name, params)

        return response
