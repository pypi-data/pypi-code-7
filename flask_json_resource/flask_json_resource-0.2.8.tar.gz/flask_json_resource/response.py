import json

from flask import Response, request


DEFAULT_HEADERS = {
    'Link': []
}


class ErrorResponse(Response):
    """ Response class that is returned when an exception is raised during
    the execution of the view.

    Returns json containing a description of the error and a status code
    """
    def __init__(self, exception, status_code, **kwargs):
        headers = {
            'Content-Type': "application/json"
        }

        error = {
            'error': exception.message,
            'status': status_code
        }

        super(ErrorResponse, self).__init__(
            json.dumps(error), status_code,
            headers=headers, **kwargs
        )


class OptionsResponse(Response):
    """ Response that is returned for requests with the OPTION method
    """
    def __init__(self, methods, resource, header=None):
        if headers is None:
            headers = {}

        headers.update(DEFAULT_HEADERS)
        headers['Allow'] = ','.join(methods)

        headers['Link'].append('<%s>; rel=describedby' % resource.schema.url)

        return super(OptionsResponse, self).__init__('', headers=headers)


class ResourceResponse(Response):
    """ Response that is return for a correct request to a ResourceView

    Set the correct content-type, link headers, etag. If the url of the resource
    differs from the request a Location header is set.
    """
    autocorrect_location_header = False

    def __init__(self, resource, status=200, headers=None, **kwargs):
        """ Initialize the reponse.

        Sets content-type and link headers. Add an etag and makes the
        request conditional
        """
        if headers is None:
            headers = {}

        headers.update(DEFAULT_HEADERS)

        headers['Content-Type'] = resource.content_type()

        for link in [
                link for link in resource.links() if link['rel'] != 'self'
        ]:
            headers['Link'].append(
                '<%s>; rel=%s' % (resource.rel(link['rel']), link['rel'])
            )

        if resource.url != request.path:
            headers['Location'] = resource.url

        super(ResourceResponse, self).__init__(
            json.dumps(resource, indent=4), status, headers=headers, **kwargs
        )

        try:
            self.set_etag(resource.etag)
        except KeyError:
            pass

        if 'last-modified' in resource.meta:
            self.last_modified = resource.meta['last-modified']

        self.make_conditional(request)


class DeleteResponse(Response):
    """ Empty response that is returned for DELETE requests."""
    def __init__(self, resource, status=204, **kwargs):
        super(DeleteResponse, self).__init__('', status)
