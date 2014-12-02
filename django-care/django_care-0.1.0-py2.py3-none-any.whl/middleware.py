""" Middlewares. """

from care.models import request_data


class AnnotateSQLMiddleware(object):

    """ Middleware that stores request path in threads local data.

    It stores request path and view name (if exists) for use
    in AnnotatingCursorWrapper, which apends that data to sql queries.

    .. versionadded:: 1.1
    """

    def process_request(self, request):
        """ Store path in threads local data. """
        request_data.path = request.build_absolute_uri()

    def process_view(self, request, view_func, view_args, view_kwargs):
        """ Store view in threads local data. """
        module_name = getattr(view_func, '__module__', '<no module>')
        func_name = getattr(view_func, '__name__', '<no view>')
        request_data.view = '%s.%s' % (module_name, func_name)

    def process_response(self, request, response):
        """ Clear stored path and view. """
        request_data.path = ''
        request_data.view = ''
        return response
