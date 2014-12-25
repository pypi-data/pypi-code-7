import time
from .stream import send_time

class MeasureMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        request._cc_start_time = time.time()
        request._cc_view_name = '%s.%s' % (view_func.__module__,
                                           view_func.__name__)

    def process_response(self, request, response):
        if hasattr(request, '_cc_start_time'):
            duration = (time.time() - request._cc_start_time) * 1000  # msec

            metric = 'view.%s.%s' % (request._cc_view_name,
                                     request.method)
            send_time(metric, duration)


        return response
