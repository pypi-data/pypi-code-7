# -*- coding: utf-8 -*-

import logging
import re
import requests

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from django.views.generic import View
from requests import ConnectionError

from .recorder import SmartProxyRecorder

# Try to load Smart Proxy configuration from Django settings file
SMART_PROXIES = getattr(settings, 'SMART_PROXIES', {})

logger = logging.getLogger(__name__)


class SmartProxyView(View):

    mode = 'play'  # By default, no recording

    def load_proxy_settings(self):
        # Check that we've configured a proxy with the specified id.
        proxy_id = self.kwargs.get('proxy_id', None)
        if not proxy_id or proxy_id not in SMART_PROXIES:
            raise Http404('The specified Django Smart Proxy could not be found.')

        # Looks good... cache proxy settings in the View.
        self.proxy_id = proxy_id
        self.proxy_settings = SMART_PROXIES[self.proxy_id]

        # Validate and retrieve the host endpoint
        self.host_endpoint = self.get_host_endpoint()


    def get_host_endpoint(self):
        # Check that we've identified a host for the specified proxy, and that
        # it's a valid URL.
        host_endpoint = self.proxy_settings.get('host_endpoint', None)
        if not host_endpoint:
            raise Http404('A host has not been configured for the specified Django Smart Proxy.')
        try:
            URLValidator()(host_endpoint)
        except ValidationError as e:
            logger.exception(e)
            raise Http404('An invalid host has been configured for the specified Django Smart Proxy.')

        # Host endpoint looks good -- return the valid url.
        return host_endpoint


    def dispatch(self, request, *args, **kwargs):
        # Populate View object with relevant proxy settings
        self.load_proxy_settings()

        # Construct and cache the full source request URL
        self.destination_url = re.sub(r'.*/{0}/(.*)'.format(kwargs['proxy_id']),
                                      r'{0}\1'.format(self.host_endpoint),
                                      request.path_info)

        # Get the response from remote server and return
        try:
            response = super(SmartProxyView, self).dispatch(request, *args, **kwargs)
        except ConnectionError as e:
            response = HttpResponseBadRequest(e)

        return response


    def play(self, request):
        """
        Plays back the response to a request, based on a previously recorded
        request/response
        """
        return self.get_recorder().playback(request)


    def record(self, response):
        """
        Records the request being made and its response
        """
        self.get_recorder().record(self.request, response)


    def get_recorder(self):
        return SmartProxyRecorder(domain=url.hostname, port=(url.port or 80))


    # Implement each of the common HTTP Request Methods
    def get_remote_server_response(self, http_method):
        return http_method(self.destination_url,
                           timeout=self.proxy_settings.get('timeout', 60.0))

    def build_http_response(self, response):
        http_response = HttpResponse(
            response.text,
            status=int(response.status_code),
            content_type=response.headers['Content-Type'])

        # Copy headers to response
        for key in response.headers.keys():
            http_response[key] = response.headers[key]

        # Copy cookies to response
        for k,v in response.cookies.iteritems():
            http_response.set_cookie(k, v)

        return http_response

    def delete(self, request, *args, **kwargs):
        response = self.get_remote_server_response(requests.delete)
        return self.build_http_response(response)

    def get(self, request, *args, **kwargs):
        response = self.get_remote_server_response(requests.get)
        return self.build_http_response(response)

    def head(self, request, *args, **kwargs):
        response = self.get_remote_server_response(requests.head)
        return self.build_http_response(response)

    def options(self, request, *args, **kwargs):
        response = self.get_remote_server_response(requests.options)
        return self.build_http_response(response)

    def patch(self, request, *args, **kwargs):
        response = self.get_remote_server_response(requests.patch)
        return self.build_http_response(response)

    def post(self, request, *args, **kwargs):
        response = self.get_remote_server_response(requests.post)
        return self.build_http_response(response)

    def put(self, request, *args, **kwargs):
        response = self.get_remote_server_response(requests.put)
        return self.build_http_response(response)
