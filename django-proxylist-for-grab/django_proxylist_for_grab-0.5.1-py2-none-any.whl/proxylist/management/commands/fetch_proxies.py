# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from datetime import timedelta

from proxylist.models import Proxy, ProxyList
from proxylist import grabber
from proxylist import now


class Command(BaseCommand):
    help = 'Update proxies from remote url'

    @staticmethod
    def parse_proxies(proxy):
        grab = grabber.Grab(use_db_proxy=False)
        grab.go(proxy.url)
        content = grab.response.body

        for proxy in content.split('\n'):
            proxy = proxy.strip()

            if proxy and ':' in proxy:
                proxy_part = proxy.split('@')
                base_part = proxy_part[0].split(':')
                if len(base_part) != 2:
                    continue

                proxy, port = base_part
                if proxy and port:
                    obj, created = Proxy.objects.get_or_create(
                        hostname=proxy, port=port)

                    if len(proxy_part) == 2:
                        auth_part = proxy_part[1].split(':')
                        if len(auth_part) == 2:
                            user, password = auth_part
                            if user and password:
                                obj.user = user
                                obj.password = password
                                obj.save()

                    if created is True:
                        obj.next_check = (
                            now() - timedelta(seconds=60))
                        obj.save()

    def handle(self, *args, **options):
        for proxy in ProxyList.objects.filter(next_check__lte=now()):
            try:
                self.parse_proxies(proxy)
            except Exception, msg:
                print '>>', msg.__str__()
            proxy.next_check = (now() - timedelta(seconds=proxy.update_period))
            proxy.save()
