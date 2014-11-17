from django.conf.urls import patterns, url

from lyrical.site_calendar.views import CalendarListView, CalendarEventDetailView 

urlpatterns = patterns('',
    url(r'^(?P<sitecalendar>[a-zA-Z0-9_-]+)/$', CalendarListView.as_view(), name='calendar-index-list'),
    url(r'^(?P<sitecalendar>[a-zA-Z0-9_-]+)/(?P<sitecalendarevent>[a-zA-Z0-9_-]+)/$',
        CalendarEventDetailView.as_view(), name='calendar-detail'),
)
