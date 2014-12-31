# -*- coding: utf-8 -*-
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
from six.moves import urllib

from keystoneclient import base


class CDN(base.Resource):
    def __repr__(self):
        return "<CDN %s>" % self._info


class CDNManager(base.ManagerWithFind):
    resource_class = CDN

    def list(self):
        return self._list('/cdn/domain', 'cdn')

    def create(self, **kwargs):
        params = {'domain': kwargs}
        return self._post('/cdn/domain', params, 'cdn')

    def update(self, domain_id, **kwargs):
        params = {'domain': kwargs}
        return self._put('/cdn/domain/%s' % domain_id, params, 'cdn')

    def get(self, domain_id):
        return self._get('/cdn/domain/%s' % domain_id, 'cdn')

    def delete(self, domain_id):
        return self._delete('/cdn/domain/%s' % domain_id)

    def flow(self, domain_id):
        return self._list('/cdn/flow/%s' % domain_id, 'cdn')

    def recharge(self, project_id=None, flow=10):
        if not project_id:
            # auth to get project_id
            if not getattr(self.client._ksclient, 'project_id', None):
                self.client._ksclient = self.client._get_ksclient(
                    **self.client.kwargs)
            project_id = self.client._ksclient.project_id
        params = {'flow': flow}
        return self._post('/recharge/%s/cdn_flow' % project_id, params, 'cdn')

    def create_urls(self, urls):
        params = {'urls': urls}
        return self._post('/cdn/urls', params, 'cdn')

    def list_urls(self):
        return self._list('/cdn/urls', 'cdn')

    def delete_urls(self, url_id):
        return self._delete('/cdn/urls/%s' % url_id)

    def cache_flush(self, domain_id=None, urls=None, dirs=None):
        domain = {}
        if domain_id:
            domain['domain_id'] = domain_id
        if urls:
            domain['urls'] = urls
        if dirs:
            domain['dirs'] = dirs
        return self._put('/cdn/cache_flush', {'domain': domain}, 'cdn')

    def request_log(self, domain_id, type, start_at=None, end_at=None):
        params = {'domain_id': domain_id, 'type': type}
        if start_at:
            params['start_at'] = start_at.isoformat()
        if end_at:
            params['end_at'] = end_at.isoformat()

        query = ''
        if params:
            query = "?" + urllib.parse.urlencode(params)
        return self._list('/cdn/request_log%s' % query, 'cdn')

    def prefetch(self, urls):
        params = {'urls': urls}
        return self._put('/cdn/prefetch', params, 'cdn')

    def prefetch_query(self, prefetch_id):
        return self._get('/cdn/prefetch/%s' % prefetch_id, 'cdn')
