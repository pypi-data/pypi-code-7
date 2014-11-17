import datetime
from django.test import TestCase
from models import SiteCalendar, SiteCalendarEvent, SiteCalendarEventManager
from django.contrib.sites.models import Site
import pytz

class ScheduleTestCase(TestCase):
    def assertOrder(self, events, order):
        self.assertEquals(len(events), len(order))
        for e, o, i in zip(events, order, range(len(events))):
            self.assertEquals(e.title, o, 'Event {} failed ({} vs {})'
                    .format(i, [e.title for e in events], order))

    def setUp(self):
        s = Site.objects.create(domain='', name='ab')
        c = SiteCalendar.objects.create(site=s, code='test', title='T')
        def mk_cal(title, *args, **kwargs):
            SiteCalendarEvent.objects.create(calendar=c, title=title,
                    slug=title, start_date=datetime.datetime(*args,
                        tzinfo=pytz.utc), 
                    **kwargs)

        mk_cal('a', 2000, 3, 1, 15)
        mk_cal('b', 2000, 3, 1, 17)
        mk_cal('c', 2000, 3, 2, 1)
        mk_cal('d', 2000, 3, 5, 16)
        mk_cal('e', 2000, 3, 5, 18)
        mk_cal('f', 2000, 4, 1, 13)
        mk_cal('g', 2000, 4, 1, 13)
        mk_cal('h', 2000, 3, 2, 13, repeat=SiteCalendarEvent.REPEAT_WEEKLY)
        mk_cal('i', 2000, 3, 4, 15, repeat=SiteCalendarEvent.REPEAT_WEEKLY)
        mk_cal('j', 2000, 3, 5, 7, repeat=SiteCalendarEvent.REPEAT_WEEKLY,
                repeat_end_date=datetime.datetime(2000, 3, 20, 7,
                tzinfo=pytz.utc))
        mk_cal('k', 2000, 3, 10, 15, repeat=SiteCalendarEvent.REPEAT_DAILY,
                repeat_end_date=datetime.datetime(2000, 3, 20, 7,
                tzinfo=pytz.utc))
        mk_cal('l', 2000, 3, 10, 15, repeat=SiteCalendarEvent.REPEAT_DAILY)

        mk_cal('m', 2000, 1, 1, 7, repeat=SiteCalendarEvent.REPEAT_DAILY,
                repeat_end_date=datetime.datetime(2000, 1, 10, 6,
                    tzinfo=pytz.utc))
        mk_cal('n', 2000, 2, 1, 7, repeat=SiteCalendarEvent.REPEAT_WEEKLY,
                repeat_end_date=datetime.datetime(2000, 2, 27, 6,
                    tzinfo=pytz.utc))

    def test_simple(self):
        s = SiteCalendarEvent.objects.schedule()
        self.assertOrder(s, ['a', 'b', 'c', 'd', 'e', 'f', 'g'])

    def test_before(self):
        s = SiteCalendarEvent.objects.schedule(before=
                datetime.datetime(2000, 3, 2, 1, tzinfo=pytz.utc))
        self.assertOrder(s, ['a', 'b', 'c'])

    def test_after(self):
        s = SiteCalendarEvent.objects.schedule(after=
                datetime.datetime(2000, 3, 2, 1, tzinfo=pytz.utc))
        self.assertOrder(s, ['c', 'd', 'e', 'f', 'g'])

    def test_prevent_infinite(self):
        def t():
            s = SiteCalendarEvent.objects.schedule(include_repeating=True)
        self.assertRaises(SiteCalendarEventManager.Error, t)

    def test_prevent_infinite_after(self):
        def t():
            s = SiteCalendarEvent.objects.schedule(after=
                    datetime.datetime(2000, 3, 2, 1, tzinfo=pytz.utc),
                    include_repeating=True)
        self.assertRaises(SiteCalendarEventManager.Error, t)

    def test_repeat_before(self):
        s = SiteCalendarEvent.objects.schedule(
                before=datetime.datetime(2000, 1, 4, 7, tzinfo=pytz.utc), 
                include_repeating=True)
        self.assertOrder(s, ['m', 'm', 'm', 'm'])

    def test_repeat_day(self):
        s = SiteCalendarEvent.objects.schedule(
                after=datetime.datetime(2000, 1, 1, 7, tzinfo=pytz.utc), 
                before=datetime.datetime(2000, 1, 7, 7, tzinfo=pytz.utc),
                include_repeating=True)
        self.assertOrder(s, ['m', 'm', 'm', 'm', 'm', 'm', 'm'])

    def test_repeat_week(self):
        s = SiteCalendarEvent.objects.schedule(
                after=datetime.datetime(2000, 2, 8, 7, tzinfo=pytz.utc), 
                before=datetime.datetime(2000, 2, 9, 7, tzinfo=pytz.utc),
                include_repeating=True)
        self.assertOrder(s, ['n'])

    def test_repeat_week_start(self):
        s = SiteCalendarEvent.objects.schedule(
                after=datetime.datetime(2000, 2, 1, 7, tzinfo=pytz.utc), 
                before=datetime.datetime(2000, 2, 2, 7, tzinfo=pytz.utc),
                include_repeating=True)
        self.assertOrder(s, ['n'])

    def test_repeat_week_many(self):
        s = SiteCalendarEvent.objects.schedule(
                after=datetime.datetime(2000, 2, 1, 7, tzinfo=pytz.utc), 
                before=datetime.datetime(2000, 2, 20, 7, tzinfo=pytz.utc),
                include_repeating=True)
        self.assertOrder(s, ['n', 'n', 'n'])

    def test_complex(self):
        s = SiteCalendarEvent.objects.schedule(
                after=datetime.datetime(2000, 3, 2, 1, tzinfo=pytz.utc), 
                before=datetime.datetime(2000, 3, 10, 14, tzinfo=pytz.utc),
                include_repeating=True)
        self.assertOrder(s, 
                ['c', 'h', 'i', 'j', 'd', 'e', 'h'])

    def test_complex2(self):
        s = SiteCalendarEvent.objects.schedule(
                after=datetime.datetime(2000, 3, 2, 1, tzinfo=pytz.utc), 
                before=datetime.datetime(2000, 3, 27, 7, tzinfo=pytz.utc),
                include_repeating=True)
        self.assertOrder(s, ['c', 
            # week
            'h', 'i', 'j', 'd', 'e', 
            # week
            'h', 'k', 'l', 'i', 'k', 'l', 'j', 
                'k', 'l', 'k', 'l', 'k', 'l', 'k', 'l', 
            # week
            'h', 'k', 'l', 'k', 'l', 'i', 'k', 'l', 
                'j', 'k', 'l', 'k', 'l', 'l', 'l', 
            # week
            'h', 'l', 'l', 'i', 'l', 'l'
            ])

    def test_repeat_week_start(self):
        s = SiteCalendarEvent.objects.schedule(
                after=datetime.datetime(2000, 2, 1, 0, tzinfo=pytz.utc), 
                before=datetime.datetime(2000, 2, 2, 0, tzinfo=pytz.utc),
                include_repeating=True)
        self.assertOrder(s, ['n'])

