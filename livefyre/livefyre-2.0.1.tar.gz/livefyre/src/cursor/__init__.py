import datetime

from livefyre.src.api.personalizedstream import PersonalizedStream
from .model import CursorData
from .validator import CursorValidator


class TimelineCursor(object):
    def __init__(self, core, data):
        self.core = core
        self.data = data
        
    @staticmethod
    def init(core, resource, limit, date):
        data = CursorData(resource, limit, date)
        return TimelineCursor(core, CursorValidator().validate(data))
    
    #slight deviation from other libraries as python3.0+ gets confused by next()
    def next_items(self):
        data = PersonalizedStream.get_timeline_stream(self, True)
        cursor = data['meta']['cursor']
        
        self.data.hasNext = cursor['hasNext']
        self.data.hasPrevious = cursor['next'] is not None
        if self.data.hasPrevious:
            self.data.cursor_time = cursor['next']

        return data
        
    def previous_items(self):
        data = PersonalizedStream.get_timeline_stream(self, False)
        cursor = data['meta']['cursor']
        
        self.data.hasPrevious = cursor['hasPrev']
        self.data.hasNext = cursor['prev'] is not None
        if self.data.hasNext:
            self.data.cursor_time = cursor['prev']

        return data
