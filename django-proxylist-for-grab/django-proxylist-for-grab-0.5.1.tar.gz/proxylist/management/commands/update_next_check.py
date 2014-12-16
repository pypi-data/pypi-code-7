# -*- coding: utf-8 -*-

from datetime import timedelta

from django.core.management.base import BaseCommand

from proxylist.models import Proxy
from proxylist import now


class Command(BaseCommand):
    help = 'Unset next check time'

    def handle(self, *args, **options):
        next_check = now() - timedelta(days=30)
        for p in Proxy.objects.all():
            p.next_check = next_check
            p.save()
