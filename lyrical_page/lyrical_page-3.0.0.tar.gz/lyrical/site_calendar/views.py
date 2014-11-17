from django.views.generic import ListView, DetailView
from django.http import Http404
import datetime

from lyrical.site_calendar.models import SiteCalendar, SiteCalendarEvent


class CalendarListView(ListView):
    model = SiteCalendarEvent
    template_name = 'site_calendar/index_list.html'
    context_object_name = 'sitecalendarevents'

    def get_queryset(self):
        cal = SiteCalendar.objects.get(code=self.kwargs.get('sitecalendar'))
        return SiteCalendarEvent.objects.schedule(
                calendar=cal,
                after=datetime.datetime.today())


class CalendarEventDetailView(DetailView):
    model = SiteCalendarEvent
    template_name = 'site_calendar/event_detail.html'
    context_object_name = 'sitecalendarevent'

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.
        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """
        
        try:
            obj = SiteCalendarEvent.objects.get(
                    calendar__code=self.kwargs.get('sitecalendar'), 
                    slug=self.kwargs.get('sitecalendarevent'))
        except SiteCalendarEvent.DoesNotExist:
            raise Http404('No event found')
        
        return obj
