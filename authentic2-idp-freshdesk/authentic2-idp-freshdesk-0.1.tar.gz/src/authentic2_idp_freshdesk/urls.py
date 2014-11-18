from django.conf.urls import patterns, url

from authentic2.decorators import setting_enabled, required

from . import app_settings

urlpatterns = required(
        setting_enabled('ENABLE', settings=app_settings),
        patterns('',
            url('^idp/freshdesk/login/', 'authentic2_idp_freshdesk.views.authenticate',
                name='idp-freshdesk-authenticate'),
        )
)
