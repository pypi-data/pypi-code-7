from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.decorators.csrf import requires_csrf_token

from lyrical.site_content.models import SitePage


class SitePageView(TemplateView):
    def get_sitepage(self, url):
        if url == '/':
            try:
                return SitePage.objects.get(is_index=True, site__id=settings.SITE_ID)
            except SitePage.DoesNotExist:
                pass

        try:
            return SitePage.objects.get(url=url, site__id=settings.SITE_ID)
        except SitePage.DoesNotExist:
            pass

        try:
            return SitePage.objects.get(sitepagealias__url_alias=url)
        except SitePage.DoesNotExist:
            pass

        return None

    def dispatch(self, request, *args, **kwargs):
        url = request.path_info
        if not url == '/':
            if not url.endswith('/') and settings.APPEND_SLASH:
                url = '%s/' % url
            if not url.startswith('/'):
                url = '/%s' % url

        self.sitepage = self.get_sitepage(url)


        if not self.sitepage:
            try:
                redirect_path = SitePage.objects.get(sitepageredirect__url=url)
                return HttpResponseRedirect(redirect_path.url)
            except SitePage.DoesNotExist:
                if 'site_seo' in settings.INSTALLED_APPS:
                    import lyrical.site_seo
                    if  site_seo.settings.SITE_SEO_ENABLED:
                        site_seo.common.add_404_url(request)
                raise Http404

        if self.sitepage.login_required and not request.user.is_authenticated():
            return redirect_to_login(self.request.path)

        return super(SitePageView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SitePageView, self).get_context_data(**kwargs)

        if getattr(self.request, 'site_seo', False):
            self.sitepage.meta_keywords = self.request.site_seo['seo_keywords']
            self.sitepage.meta_description = self.request.site_seo['seo_description']

        context_dict = {'sitepage': self.sitepage, 'request_path': self.request.path}
        context_dict.update(context)
        return context_dict

    def get_template_names(self):
        if self.sitepage.custom_template:
            template_path = self.sitepage.custom_template
        elif self.sitepage.template:
            template_path = self.sitepage.template.template_path
        else:
            template_path = 'site_content/site_page.html'

        # FIXME: This should evaluated for better handling
        return [template_path]
