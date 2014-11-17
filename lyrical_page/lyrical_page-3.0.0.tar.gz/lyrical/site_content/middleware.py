from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.http import Http404 
from django.template.response  import TemplateResponse

from lyrical.site_content.views import SitePageView


def make_tls_property(default=None):
    """Creates a class-wide instance property with a thread-specific value."""
    class TLSProperty(object):
        def __init__(self):
            from threading import local
            self.local = local()

        def __get__(self, instance, cls):
            if not instance:
                return self
            return self.value

        def __set__(self, instance, value):
            self.value = value

        def _get_value(self):
            return getattr(self.local, 'value', default)

        def _set_value(self, value):
            self.local.value = value
        value = property(_get_value, _set_value)

    return TLSProperty()

 
def _patch_setattr(obj):
    """Purpose of this is to allow changes to settings object again after it is
    changed to tls property.

    Without this patch the following is not possible::

        settings.SITE_ID = 1
        settings.SITE_ID = 42
        assert settings.SITE_ID == 42 # this fails without this patch

    """
    old_setattr = obj.__setattr__
    def wrap_setattr(self, name, value):
        try:
            getattr(self.__class__, name).value = value
        except AttributeError:
            old_setattr(name, value)
    obj.__class__.__setattr__ = wrap_setattr
_patch_setattr(settings)
 
_default_site_id = getattr(settings, 'SITE_ID', None)
settings.__class__.SITE_ID = make_tls_property()


class SitePageFallbackMiddleware(object):
    def process_request(self, request):
        # Ignore port if it's 80 or 443
        if ':' in request.get_host():
            domain, port = request.get_host().split(':')
            if int(port) not in (80, 443, 8080):
                domain = request.get_host()
        else:
            domain = request.get_host().split(':')[0]

        # Domains are case insensitive
        domain = domain.lower()

        # We cache the SITE_ID
        cache_key = 'LyricalPage:Site:domain:%s' % domain
        site = cache.get(cache_key)
        if site:
            settings.SITE_ID = site
        else:
            try:
                site = Site.objects.get(domain=domain)
            except Site.DoesNotExist:
                site = None

            if not site:
                # Fall back to with/without 'www.'
                if domain.startswith('www.'):
                    fallback_domain = domain[4:]
                else:
                    fallback_domain = 'www.' + domain

                try:
                    site = Site.objects.get(domain=fallback_domain)
                except Site.DoesNotExist:
                    site = None

            # Add site if it doesn't exist
            if not site and getattr(settings, 'CREATE_SITES_AUTOMATICALLY',
                                    False):
                site = Site(domain=domain, name=domain)
                site.save()

            # Set SITE_ID for this thread/request
            if site:
                settings.SITE_ID = site.pk
            else:
                settings.SITE_ID = _default_site_id

            cache.set(cache_key, settings.SITE_ID, 5 * 60)

    def process_response(self, request, response):
        if response.status_code != 404:
            return response

        try:
            response = SitePageView.as_view()(request)
            if isinstance(response, TemplateResponse):
                response.render()
            return response

        except Http404:
            if 'site_seo' in settings.INSTALLED_APPS:
                import lyrical.site_seo.common
                site_seo.common.add_404_url(request)

            return response
        except:
            if settings.DEBUG:
                raise

            return response
