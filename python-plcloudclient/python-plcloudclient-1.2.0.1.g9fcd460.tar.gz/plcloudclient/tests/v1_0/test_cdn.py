# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
import random

from plcloudclient.tests.v1_0 import utils
from plcloudclient.v1_0 import cdn


class CDNTests(utils.TestCase):

    def test_list(self):
        refs = self.client.cdn.list()
        print refs
        self.assertIsInstance(refs, list)
        if refs:
            self.assertIsInstance(refs[0], cdn.CDN)

    def test_get(self):
        ref = self.client.cdn.get('123123')
        self.assertIsInstance(ref, cdn.CDN)

    def test_create(self):
        domain = {'domain': '%s.plcloud.com' % random.randint(10000, 99999),
                  'origin_ips': ['114.119.4.141'],
                  'areas': ['cn'], 'type': 'web'}
        ref = self.client.cdn.create(**domain)
        self.assertIsInstance(ref, cdn.CDN)

    def test_delete(self):
        ref = self.client.cdn.delete('206800')
        print ref
        self.assertIsInstance(ref, tuple)

    def test_update(self):
        domain = {'enable': False}
        ref = self.client.cdn.update('206783', **domain)
        self.assertIsInstance(ref, cdn.CDN)

    def test_recharge(self):
        ref = self.client.cdn.recharge('26c151adb9fe4bb68de705acf6e76d24', 10)
        print ref
        self.assertIsInstance(ref, cdn.CDN)

    def gen_url(self, domain='plcloud.com', schema='http'):
        characters = '0123456789abcdefghijklmnopqrstuvwxyz'
        is_file = random.randint(0, 1)
        path = '/'.join(
            ''.join(random.choice(characters) for _x in xrange(random.randint(3, 10))) for i in xrange(random.randint(3, 10)))  # noqa
        if is_file:
            name = '%s.%s' % (
                ''.join(random.choice(characters) for _x in xrange(
                    random.randint(3, 10))),
                ''.join(random.choice(characters) for _x in xrange(
                    random.randint(2, 4))))
            return '%s://%s/%s/%s' % (schema, domain, path, name)
        return '%s://%s/%s' % (schema, domain, path)

    def test_create_urls(self):
        urls = [self.gen_url('joe.com') for i in range(1000)]
        refs = self.client.cdn.create_urls(urls)
        print refs
        self.assertIsInstance(refs, cdn.CDN)

    def test_list_urls(self):
        refs = self.client.cdn.list_urls()
        print refs
        self.assertIsInstance(refs, list)
        if refs:
            self.assertIsInstance(refs[0], cdn.CDN)

    def test_delete_urls(self):
        refs = self.client.cdn.list_urls()
        for i in refs[:10]:
            refs = self.client.cdn.delete_urls(i.id)
        print refs
        self.assertIsInstance(refs, tuple)
        if refs:
            self.assertIsInstance(refs[1], dict)
