from __future__ import unicode_literals

from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.utils.encoding import iri_to_uri
from django.utils.http import urlquote
from django.core.exceptions import ImproperlyConfigured

import hashlib
import hmac
import time

def import_class(full_name):
    """ Imports a class by its str path
    :param full_name ex: "path.to.my.class"
    :rtype class
    """
    mod_name, class_name = full_name.rsplit('.', 1)
    mod = __import__(mod_name, fromlist=[class_name])
    return getattr(mod, class_name)

@never_cache
@login_required
def authenticate(request):
    """ Code derived from https://github.com/ThatGreenSpace/django-freshdesk
    Copyright (c) 2014 That Green Space Pte Ltd and individual contributors.
    All rights reserved.
    """
    if not hasattr(settings, 'FRESHDESK_URL'):
        raise ImproperlyConfigured("Set the FRESHDESK_URL settings variable")
    if not hasattr(settings, 'FRESHDESK_SECRET_KEY'):
        raise ImproperlyConfigured("Set the FRESHDESK_SECRET_KEY settings variable")

    if not request.user:
        raise Http404()

    first_name = request.user.first_name
    last_name = request.user.last_name
    username = request.user.get_username()
    full_name = '{0} {1}'.format(first_name, last_name) if first_name or last_name else username

    utctime = int(time.time())
    data = '{0}{1}{2}'.format(
        full_name, request.user.email, utctime)
    generated_hash = hmac.new(
        settings.FRESHDESK_SECRET_KEY.encode(), data.encode('utf-8'), hashlib.md5).hexdigest()
    url = '{0}/login/sso?name={1}&email={2}&timestamp={3}&hash={4}'.format(
        settings.FRESHDESK_URL.strip('/'),
        urlquote(full_name), urlquote(request.user.email), utctime, generated_hash)

    # If configured, we have an option to divert the user based on his email to
    # an url insetad of the freshdesk.
    if hasattr(settings, 'FRESHDESK_DIVERT_CLASS'):
        diverter = (import_class(settings.FRESHDESK_DIVERT_CLASS))()
        if diverter.should_divert(request.user):
            return HttpResponseRedirect(diverter.divert_url(request.user, request))

    return HttpResponseRedirect(iri_to_uri(url))
