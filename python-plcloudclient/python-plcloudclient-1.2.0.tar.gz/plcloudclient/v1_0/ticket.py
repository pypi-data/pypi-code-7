# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
from keystoneclient import base


class Ticket(base.Resource):
    def __repr__(self):
        return "<Ticket %s>" % self._info


class TicketManager(base.ManagerWithFind):
    resource_class = Ticket

    def list(self, user_id=None):
        if user_id:
            url = '/ticket/%s/list' % user_id
        else:
            url = '/ticket'
        return self._list(url, 'ticket')

    def get(self, ticket_id):
        return self._get('/ticket/%s' % ticket_id, 'ticket')

    def create(self, summary, description):
        params = {'summary': summary,
                  'description': description}
        return self._post('/ticket', params, 'ticket')

    def update(self, ticket_id, status):
        params = {'status': status}
        return self._put('/ticket/%s' % ticket_id, params, 'ticket')

    def list_reply(self, ticket_id):
        return self._list('/ticket/reply/%s' % ticket_id, 'ticket')

    def reply(self, ticket_id, content):
        params = {'content': content}
        return self._post('/ticket/reply/%s' % ticket_id, params, 'ticket')
