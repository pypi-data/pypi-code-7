from django.conf.urls import *

urlpatterns = patterns('nano.faq.views',
        (r'^$',                     'list_faqs'),
)
