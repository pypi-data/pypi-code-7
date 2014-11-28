import time
import re

from gapi import GoogleAPI
from gapicalendar import GoogleCalendar

# gapi=GoogleAPI(secretsFile, credentialsFile, [
#     'https://www.googleapis.com/auth/calendar',
#     'https://www.googleapis.com/auth/calendar.readonly'])

class GoogleCalendarScheduler(object):
    def __init__(self, gapi, calendarId, preheatingtime=0):
        self._gapi = gapi
        self._cal=GoogleCalendar(self._gapi, calendarId)
        self._cal.setPreheatingTime(preheatingtime)
        self._events=[]
        self._stampEvents=0

    @property
    def gapi(self):
        return self._gapi

    def authenticate(self):
        return self._gapi.authenticate()

    def age(self):
        return time.time()-self._stampEvents

    def refreshEvents(self, dt):
        if self.authenticate():
            t=time.time()
            try:
                events=self._cal.getEvents(t-3600*24, t+dt, False)
                self._stampEvents=t
                self._events=events
                return True
            except:
                pass

    def getActiveEvents(self, dt=3600*24*7):
        if self.age()>=60:
            self.refreshEvents(dt)
        return self._cal.extractActiveEvents(self._events)

    def getActiveEvent(self, dt=3600*24*7):
        events=self.getActiveEvents(dt)
        try:
            if events:
                return events[-1]
        except:
            pass

    def extractConsignFromString(self, s, vmin, vmax):
        try:
            if s:
                # normalize a bit the give string
                s=s.lower()

                # convert degree to something like "21.2oC"
                s=re.sub(r'\xc2c', 'oc', s)
                s=re.sub(r'\xc2', 'oc', s)

                # first search for 21.3oC or 21.3C string ...
                m=re.search(r'\b(\d+(?:(?:\.|,)\d+)?)\s?(?:(?:oc)|c)\b', s)
                if not m:
                    # if not found search for 21.3 (can be confusing if number in text)
                    m=re.search(r'\b(\d\d(?:(?:\.|,)\d)?)\b', s)

                if m:
                    c=m.group(1)
                    c=c.replace(',', '.')
                    v=float(c)
                    if v>=float(vmin) and v<=float(vmax):
                        return v
        except:
            pass

    def guessConsignFromEvent(self, event, vmin=12.0, vmax=28.0, defaultValue=None):
        if event:
            c=self.extractConsignFromString(event.location, vmin, vmax)
            if c is None:
                c=self.extractConsignFromString(event.description, vmin, vmax)
            if c is None:
                c=self.extractConsignFromString(event.title, vmin, vmax)
            if c is not None:
                return c

        return defaultValue


if __name__ == '__main__':
    pass
