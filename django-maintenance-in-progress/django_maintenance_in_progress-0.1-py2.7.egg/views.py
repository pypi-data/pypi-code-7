import os

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.defaults import server_error as base_server_error
from django.views.decorators.csrf import requires_csrf_token

from maintenance_in_progress.models import Preferences


def server_error(request, template_name="maintenance_in_progress/500.html"):
    """If maintenance is in progress render a friendly page"""
    p = Preferences.objects.get()
    if p.in_progress or (p.file_marker and os.path.exists(p.file_marker)):
        # Set immediate expiry time because we're effectively returning the
        # wrong content with status code 200.
        response = render_to_response(
            template_name,
            {},
            context_instance=RequestContext(request)
        )
        response["Expires"] = -1
        return response
    return base_server_error(request)
