"""URLs to run the tests."""
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


admin.autodiscover()

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

urlpatterns += patterns(
    '',
    url(r'purchasing/', include('aps_purchasing.urls')),
    url(r'^bom/', include('aps_bom.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
