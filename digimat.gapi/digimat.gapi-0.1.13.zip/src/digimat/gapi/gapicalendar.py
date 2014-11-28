import time
import re
import sys, traceback

import pprint

#pip install strict_rfc3339
#https://pypi.python.org/pypi/strict-rfc3339/
import strict_rfc3339

# TIP: to display a shared calendar on a mobile device,
# go to https://www.google.com/calendar/syncselect and enable them.

class GoogleCalendarEvent(object):
    def __init__(self, gevent, preheatingtime=0):
        self._json=gevent
        self._start=None
        self._end=None
        self._valid=False
        self._preheatingtime=preheatingtime
        self.loadFromJson()

    def __getitem__(self, key):
        try:
            return self._json[key]
        except:
            pass

    def __cmp__(self, other):
        return cmp(self.start, other.start)

    def getstr(self, key):
        s=self[key]
        if s:
            return s.encode('utf-8').strip()
        return ''

    @property
    def id(self):
        return self['id']

    @property
    def title(self):
        return self._title

    @property
    def location(self):
        return self._location

    @property
    def description(self):
        return self._description

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    def isRecurrent(self):
        return self['recurrence']

    def isTimeSlot(self):
        try:
            if self['start']['dateTime']:
                return True
        except:
            pass

    def isDaySlot(self):
        return not self.isTimeSlot()

    def isActive(self, t=None):
        if not t:
            t=time.time()

        start=self.start
        if self.isTimeSlot():
            start-=abs(self._preheatingtime)

        end=self.end

        if t>=start and t<=end:
            return True

    def validate(self):
        self._valid=True
        if not self.start or not self.end:
            self._valid=False

    def loadFromJson(self):
        self._title=self.getstr('summary')
        self._location=self.getstr('location')
        self._description=self.getstr('description')

        try:
            self._start=strict_rfc3339.rfc3339_to_timestamp(self['start']['dateTime'])
            self._end=strict_rfc3339.rfc3339_to_timestamp(self['end']['dateTime'])
        except:
            try:
                self._start=time.mktime(time.strptime(self['start']['date'], '%Y-%m-%d'))
                self._end=time.mktime(time.strptime(self['end']['date'], '%Y-%m-%d'))
            except:
                #traceback.print_exc(file=sys.stdout)
                #pprint.pprint(self._json)
                pass

        self.validate()


    def isValid(self):
        return self._valid

    def __str__(self):
        return '(%s<->%s):%s' % (
            strict_rfc3339.timestamp_to_rfc3339_localoffset(self.start),
            strict_rfc3339.timestamp_to_rfc3339_localoffset(self.end),
            self.title)

    def dump(self):
        pprint.pprint(self._json)


class GoogleCalendar(object):
    def __init__(self, gapi, calendarId):
        self._gapi=gapi
        self._calendarId=calendarId
        self._preheatingtime=0

    @property
    def gapi(self):
        return self._gapi

    def service(self):
        # https://developers.google.com/google-apps/calendar/?hl=fr
        return self.gapi.service('calendar', 'v3')

    def setPreheatingTime(self, t):
        self._preheatingtime=abs(t)

    def getEventInstances(self, eventId, timeFrom, timeTo, activeOnly=False):
        events=[]
        page_token = None
        while True:
            df=strict_rfc3339.timestamp_to_rfc3339_utcoffset(timeFrom)
            dt=strict_rfc3339.timestamp_to_rfc3339_utcoffset(timeTo)

            try:
                gevents = self.service().events().instances(
                    calendarId=self._calendarId,
                    eventId=eventId,
                    pageToken=page_token,
                    timeMin=df,
                    timeMax=dt).execute()

                for gevent in gevents['items']:
                    e=GoogleCalendarEvent(gevent, self._preheatingtime)
                    if not activeOnly or e.isActive():
                        if e.isValid():
                            events.append(e)

                page_token = gevents.get('nextPageToken')
                if not page_token:
                    break
            except:
                traceback.print_exc(file=sys.stdout)
                break

        return events

    def getEvents(self, timeFrom, timeTo, activeOnly=False):
        events=[]
        page_token = None
        while True:
            df=strict_rfc3339.timestamp_to_rfc3339_utcoffset(timeFrom)
            dt=strict_rfc3339.timestamp_to_rfc3339_utcoffset(timeTo)

            try:
                gevents = self.service().events().list(
                    calendarId=self._calendarId,
                    pageToken=page_token,
                    timeMin=df,
                    timeMax=dt).execute()

                for gevent in gevents['items']:
                    e=GoogleCalendarEvent(gevent, self._preheatingtime)
                    if e.isRecurrent():
                        events=events+self.getEventInstances(e.id, timeFrom, timeTo, activeOnly)
                    else:
                        if not activeOnly or e.isActive():
                            if e.isValid():
                                events.append(e)

                page_token = gevents.get('nextPageToken')
                if not page_token:
                    break
            except:
                #traceback.print_exc(file=sys.stdout)
                raise Exception("getEvents() error!")
                break

        return sorted(events)

    def extractActiveEvents(self, events):
        eventsActive=[]
        for event in events:
            if event.isActive():
                eventsActive.append(event)
        return sorted(eventsActive)

if __name__ == '__main__':
    pass
