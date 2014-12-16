# -*- coding: utf-8 -*-

from django.core.cache import cache
from celery.task import Task
from celery import task

from management.commands.check_proxies import check_proxies
from management.commands.clean_proxies import clean_proxies
from management.commands.grab_proxies import grab_proxies


@task(ignore_result=True, time_limit=30)
def async_check(proxy_pk, mirror_pk):
    from models import Proxy, Mirror

    mirror = Mirror.objects.get(pk=mirror_pk)
    mirror._check_proxy(Proxy.objects.get(pk=proxy_pk))


def run_and_lock(foo, task):
    lock_key = str(task.__name__)

    if cache.get(lock_key) is None:
        cache.set(lock_key, True, 3600)
        try:
            foo()
            cache.delete(lock_key)
        except Exception:
            cache.delete(lock_key)
            raise
    else:
        print 'still working ...'


class CleanProxies(Task):
    def run(self, *args, **kwargs):
        run_and_lock(clean_proxies, self)


class GrabProxies(Task):
    ignore_result = True
    send_error_emails = False

    def run(self, *args, **kwargs):
        run_and_lock(grab_proxies, self)


class CheckProxies(Task):
    def run(self, *args, **kwargs):
        run_and_lock(check_proxies, self)
