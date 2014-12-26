# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
import logging

from keystoneclient.v2_0 import client as ksclient
from keystoneclient import exceptions
from keystoneclient.openstack.common import jsonutils
from keystoneclient import baseclient
from keystoneclient.auth import base
from keystoneclient import session as client_session

from plcloudclient.v1_0 import ticket
from plcloudclient.v1_0 import cdn

LOG = logging.getLogger(__name__)


class Client(baseclient.Client, base.BaseAuthPlugin):
    version = 'v1.0'

    def __init__(self, **kwargs):
        self.ticket = ticket.TicketManager(self)
        self.cdn = cdn.CDNManager(self)

        self.allow_reauth = kwargs.get('allow_reauth', False)
        self.token = kwargs.get('token')
        self.endpoint = kwargs.get('endpoint')
        self.endpoint_type = kwargs.get('endpoint_type', 'publicURL')
        self._ksclient = None
        self.kwargs = kwargs
        self.region_name = kwargs.get('region_name')

        session = client_session.Session.construct(kwargs)
        session.auth = self

        super(Client, self).__init__(session)

    def _get_ksclient(self, **kwargs):
        return ksclient.Client(username=kwargs.get('username'),
                               password=kwargs.get('password'),
                               tenant_id=kwargs.get('tenant_id'),
                               tenant_name=kwargs.get('tenant_name'),
                               auth_url=kwargs.get('auth_url'),
                               region_name=kwargs.get('region_name'),
                               cacert=kwargs.get('cacert'),
                               insecure=kwargs.get('insecure'))

    def get_token(self, session):
        if self.token:
            return self.token
        if not self._ksclient:
            self._ksclient = self._get_ksclient(**self.kwargs)
        return self._ksclient.auth_token

    def get_endpoint(self, session, **endpoint_filter):
        if self.endpoint:
            return self.endpoint
        if not self._ksclient:
            self._ksclient = self._get_ksclient(**self.kwargs)
        return self._ksclient.service_catalog.url_for(**endpoint_filter)

    @staticmethod
    def _decode_body(resp):
        if resp.text:
            try:
                body_resp = jsonutils.loads(resp.text)
            except (ValueError, TypeError):
                body_resp = None
                LOG.debug("Could not decode JSON from body: %s",
                          resp.text)
        else:
            LOG.debug("No body was returned.")
            body_resp = None

        return body_resp

    def request(self, url, method, **kwargs):
        try:
            kwargs['json'] = kwargs.pop('body')
        except KeyError:
            pass

        endpoint_filter = kwargs.setdefault('endpoint_filter', {})
        endpoint_filter.setdefault('service_type', 'plcloud')
        endpoint_filter.setdefault('endpoint_type', self.endpoint_type)
        endpoint_filter.setdefault('service_name', 'plcloud')
        if self.region_name:
            endpoint_filter.setdefault('region_name', self.region_name)

        if self.endpoint and not self.token:
            kwargs['authenticated'] = False
        try:
            resp = super(Client, self).request(url, method, **kwargs)
        except exceptions.Unauthorized:
            if self.allow_reauth:
                self._ksclient = self._get_ksclient(**self.kwargs)
                resp = super(Client, self).request(url, method, **kwargs)
            else:
                raise
        return resp, self._decode_body(resp)
