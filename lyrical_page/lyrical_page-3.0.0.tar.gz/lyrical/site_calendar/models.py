import datetime
import collections

from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

class SiteCalendar(models.Model):
    site = models.ForeignKey(Site)
    code = models.SlugField(help_text='Used in templates and urls', 
            max_length=255, unique=True)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'site calendars'
    
    def __unicode__(self):
        return u'{0}'.format(self.title)

class SiteCalendarEventManager(models.Manager):
    class Error(Exception):
        pass

    def repeating(self, calendar=None, after=None, before=None):
        if not before:
            raise SiteCalendarEventManager.Error

        qs = SiteCalendarEvent.objects
        if calendar:
            qs = qs.filter(calendar=calendar)

        repeat = qs.order_by('start_date').filter(start_date__lte=before)
        if after:
            repeat = list(repeat.filter(Q(repeat_end_date__gte=after) 
                    | Q(repeat_end_date=None)))

            if not repeat:
                return []

            date = max(after, repeat[0].start_date)
        else:
            if len(repeat) > 0:
                date = repeat[0].start_date
            else:
                return []

        # introspect faux-event tuple for display
        event_fields = [f.name for f in SiteCalendarEvent._meta.fields]

        def make_repeat(event, date):
            attr = dict([(n, getattr(event, n)) for n in event_fields])
            attr['start_date'] = datetime.datetime(date.year, date.month, date.day, 
                    event.start_date.hour, event.start_date.minute, 
                    event.start_date.second, tzinfo=event.start_date.tzinfo)
            return RepeatedSiteCalendarEvent(**attr)
        
        day = datetime.timedelta(days=1)
        events = []
        while date <= before:
            for event in repeat:
                if (event.start_date > date + datetime.timedelta(days=1) 
                        or (event.repeat_end_date and event.repeat_end_date < date)):
                    continue

                if event.repeat == SiteCalendarEvent.REPEAT_DAILY:
                    events += [make_repeat(event, date)]
                elif (event.repeat == SiteCalendarEvent.REPEAT_WEEKLY
                        and event.start_date.weekday() == date.weekday()):
                    events += [make_repeat(event, date)]
            date = date + day

        # remove any events that are past the end
        try:
            while events[-1].start_date > before:
                events = events[:-1]
            return events
        except IndexError:
            return []


    def schedule(self, calendar=None, after=None, before=None, include_repeating=False):
        """ Returns a list of events meeting the given criteria. """

        if include_repeating and not before:
            raise SiteCalendarEventManager.Error

        qs = SiteCalendarEvent.objects
        if calendar:
            qs = qs.filter(calendar=calendar)

        no_repeat = qs.filter(repeat=SiteCalendarEvent.REPEAT_NONE)
        if after:
            no_repeat = no_repeat.filter(start_date__gte=after)
        if before:
            no_repeat = no_repeat.filter(start_date__lte=before)

        if not include_repeating:
            return no_repeat.order_by('start_date')

        repeating =  self.repeating(calendar=calendar, after=after,
                before=before)
        events=list(no_repeat) + repeating
        events.sort(key=lambda e: e.start_date)
        return events


class SiteCalendarEvent(models.Model):
    DAYS = ('Monday', 'Tuesday', 'Wednesday', 
            'Thursday', 'Friday', 'Saturday', 'Sunday')
    REPEAT_NONE = 0
    REPEAT_DAILY = 1
    REPEAT_WEEKLY = 2
    REPEAT_CHOICES = (
            (REPEAT_NONE, "Once Only"),
            (REPEAT_DAILY, "Every Day"),
            (REPEAT_WEEKLY, "Every Week"),
            )

    calendar = models.ForeignKey(SiteCalendar)
    title = models.CharField(max_length=255)
    slug = models.SlugField(help_text='Used in url', max_length=255, unique=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    publish_date = models.DateTimeField(default=timezone.now,
            null=True)
    published = models.BooleanField(default=True)
    css_class = models.CharField(max_length=50, blank=True)

    # scheduling
    start_date = models.DateTimeField()
    repeat = models.IntegerField(default=REPEAT_NONE)
    repeat_end_date = models.DateTimeField('Stop Repeating At', blank=True, null=True)
    def repeat_human_readable(self):
        for c, desc in self.REPEAT_CHOICES:
            if c == self.repeat:
                return desc
        return ''
    repeat_human_readable.admin_order_field = 'repeat'
    repeat_human_readable.short_description = 'Repeat'

    def weekday_name(self):
        return self.DAYS[self.start_date.weekday()]

    objects = SiteCalendarEventManager()

    def get_absolute_url(self):
        return reverse('calendar-detail', args=[self.calendar.code, self.slug])

    class Meta:
        verbose_name_plural = 'site calendar events'
    
    def __unicode__(self):
        return u'{0}'.format(self.title)

class RepeatedSiteCalendarEvent(SiteCalendarEvent):
    class Meta:
        proxy = True
