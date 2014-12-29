# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
from plcloudclient.tests.v1_0 import utils
from plcloudclient.v1_0 import ticket


class TicketTests(utils.TestCase):

    def test_list(self):
        ref = self.client.ticket.list()
        print ref
        self.assertIsInstance(ref, list)
        if ref:
            self.assertIsInstance(ref[0], ticket.Ticket)

    def test_get(self):
        ref = self.client.ticket.get('tk-8b47870c')
        print ref
        self.assertIsInstance(ref, ticket.Ticket)

    def test_create(self):
        ref = self.client.ticket.create(summary='test', description='test')
        print ref
        self.assertIsInstance(ref, ticket.Ticket)

    def test_update(self):
        ref = self.client.ticket.update('tk-8b47870c', 'closed')
        print ref
        self.assertIsInstance(ref, ticket.Ticket)

    def test_create_reply(self):
        ref = self.client.ticket.create_reply('tk-8b47870c', 'joeasdf')
        print ref
        self.assertIsInstance(ref, ticket.Ticket)

    def test_list_reply(self):
        ref = self.client.ticket.list_reply('tk-8b47870c')
        print ref
        self.assertIsInstance(ref, list)
        if ref:
            self.assertIsInstance(ref[0], ticket.Ticket)
