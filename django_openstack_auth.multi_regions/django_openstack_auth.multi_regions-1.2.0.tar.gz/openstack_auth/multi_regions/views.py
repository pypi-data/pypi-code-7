# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
import logging
import json

from django.conf import settings
from django import shortcuts
from django.utils import http
from django.http import HttpResponse
from django.contrib import auth
from django.core.signing import Signer
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.translation import ugettext_lazy as _

import openstack_auth
from openstack_auth import user as auth_user
from openstack_auth import views as auth_views
from openstack_auth import utils
from openstack_auth.exceptions import KeystoneAuthException

try:
    is_safe_url = http.is_safe_url
except AttributeError:
    is_safe_url = utils.is_safe_url

LOG = logging.getLogger(__name__)


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name=None, extra_context=None, **kwargs):
    if openstack_auth.__version__ > '1.1.6':
        res = auth_views.login(request, template_name, extra_context, **kwargs)
    else:
        res = auth_views.login(request)
    if request.user.is_authenticated():
        region_endpoint = request.user.endpoint
        MULTI_REGIONS = dict((i[0], i) for i in settings.MULTI_REGIONS)
        _, region, region_name = MULTI_REGIONS.get(region_endpoint)
        request.session['region_endpoint'] = region_endpoint
        request.session['region'] = region
        request.session['region_name'] = region_name
        hash_password = Signer().sign(request.POST.get('password'))
        request.session['hash_password'] = hash_password
    return res


@login_required
def _switch_region(request, region):
    """
    Switches the non-identity services region that is being managed
    for the scoped project.
    MULTI_REGIONS = [
        ('http://10.0.0.1:5000/v2.0', 'region-1', 'region_name-1'),
        ('http://192.168.1.100:5000/v2.0', 'region-2', 'region_name-2'),
    ]
    """
    MULTI_REGIONS = dict((i[1], i) for i in settings.MULTI_REGIONS)
    if region in MULTI_REGIONS:
        region = MULTI_REGIONS[region]
        LOG.debug('Switching services region to %s for user "%s".'
                  % (region, request.user.username))
        password = Signer().unsign(request.session['hash_password'])
        username = request.user.username
        try:
            user = auth.authenticate(
                request=request,
                username=username,
                password=password,
                user_domain_name=request.user.domain_name,
                auth_url=region[0])
            request.session[auth.SESSION_KEY] = user.pk
            auth.login(request, user)
            auth_user.set_session_from_user(request, user)
            request.session['region_endpoint'] = region[0]
            request.session['region'] = region[1]
            request.session['region_name'] = region[2]
            request.session['services_region'] = region[1]
            msg = 'Login successful for user "%(username)s".' % \
                {'username': username}
            LOG.info(msg)
            return region
        except KeystoneAuthException:
            msg = 'Login failed for user "%(username)s".' % \
                {'username': username}
            LOG.warning(msg)
    return False


@login_required
def api_switch_region(request):
    """async post switch region"""
    region = json.loads(request.raw_post_data).get('region')
    available_region = _switch_region(request, region)
    if available_region:
        resp = {'code': 200, 'data': {'region': available_region[1]},
                'message': u'%s' % _('Success')}
    else:
        resp = {'code': 500, 'data': {},
                'message': u'%s' % _('Switch region fail')}

    return HttpResponse(json.dumps(resp, ensure_ascii=False),
                        content_type="application/json")


@login_required
def switch_region_external(request, region_name,
                           redirect_field_name=auth.REDIRECT_FIELD_NAME):
    """get switch region"""
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = settings.LOGIN_REDIRECT_URL
    available_region = _switch_region(request, region_name)
    if available_region:
        redirect_to = redirect_to + '?switch_region=success'
    else:
        redirect_to = redirect_to + '?switch_region=fail'
    return shortcuts.redirect(redirect_to)
