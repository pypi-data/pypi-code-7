"""
mixins.json_error

Handler mixin for writing JSON errors

"""
version_info = (1, 0, 0)
__version__ = '.'.join(str(v) for v in version_info)


class JsonErrorMixin(object):
    """Mixin to write errors as JSON."""

    def write_error(self, status_code, **kwargs):
        """Suppress the automatic rendering of HTML code upon an error.

           :param int status_code:
                The HTTP status code the :class:`HTTPError` raised.

           :param dict kwargs:
                Automatically filled with exception information including
                the error that was raised, the class of error raised, and an
                object.

        """
        _, raised_error, _ = kwargs.get('exc_info', (None, None, None))

        error_type = getattr(raised_error, 'error_type', self._reason)

        try:
            error_message = raised_error.get_message()
        except AttributeError:
            error_message = 'Unexpected Error'

        self.error = {
            'message': error_message,
            'type': error_type,
        }
        if hasattr(raised_error, 'documentation_url'):
            self.error['documentation_url'] = raised_error.documentation_url

        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.finish(self.error)
