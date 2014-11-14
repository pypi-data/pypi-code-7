import time
import re

from gapi import GoogleAPI
from gapicalendar import GoogleCalendar

class GoogleCalendarScheduler(object):
    def __init__(self, secretsFile, credentialsFile, calendarId, preheatingtime=0):
        self._gapi = GoogleAPI(secretsFile, credentialsFile, [
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.readonly'])
        self._cal=GoogleCalendar(self._gapi, calendarId)
        self._cal.setPreheatingTime(preheatingtime)
        self._events=[]
        self._stampEvents=0

    def authenticate(self):
        if not self._gapi.isAuthenticated():
            self._gapi.authenticate()

    def age(self):
        return time.time()-self._stampEvents

    def refreshEvents(self, dt):
        self.authenticate()
        t=time.time()
        try:
            events=self._cal.getEvents(t-3600*24, t+dt, False)
            self._stampEvents=t
            self._events=events
            return True
        except:
            pass

    def getActiveEvent(self, dt=3600*24*7):
        if self.age()>=60:
            self.refreshEvents(dt)
        events=self._cal.extractActiveEvents(self._events)
        try:
            if events:
                return events[-1]
        except:
            pass

    def guessConsignFromEvent(self, event, vmin=12.0, vmax=28.0, defaultValue=None):
        if event:
            # first, scan dedicated 'location+description' field
            cre=re.compile('([0-9]+[\.,]?[0-9]*) *\xc2?[cC]?')
            m=cre.match(event.location)
            if not m:
                m=cre.match(event.description)
            if m:
                c=m.group(1)
                c=c.replace(',', '.')
                v=float(c)
                if v<vmin:
                    v=float(vmin)
                if v>vmax:
                    v=float(vmax)
                return float(v)

            #second, try a more subtle 'title' string search (\xc2 == deg)
            cre=re.compile('/((\d+(?:\.|,)?\d*) ?(?:\xc2|c|\xc2c){1})/i')
            m=cre.match(event.title)
            if m:
                c=m.group(1)
                c=c.replace(',', '.')
                v=float(c)
                if v<vmin:
                    v=float(vmin)
                if v>vmax:
                    v=float(vmax)
                return float(v)

        return defaultValue


if __name__ == '__main__':
    pass
