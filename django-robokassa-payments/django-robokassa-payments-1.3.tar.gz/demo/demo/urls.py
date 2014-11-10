from django.conf.urls import patterns, url

urlpatterns = patterns(
    'demo.views',
    url(r'^$', 'pay_with_robokassa', name='pay-with-robokassa'),
)
