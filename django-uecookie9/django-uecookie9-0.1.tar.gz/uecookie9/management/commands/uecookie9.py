from django.core.management.base import BaseCommand
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

class Command(BaseCommand):
    def handle(self, *args, **options):
        url = '/cookies/'
        try:
            FlatPage.objects.get(url=url)
            raise Exception("This FlatPage has already been created.")
        except FlatPage.DoesNotExist:
            content = render_to_string('uecookie9/policy.html')
            fp = FlatPage.objects.create(url=url, title='Cookie Policy', content=content)
            fp.sites.add(Site.objects.get(id=1))