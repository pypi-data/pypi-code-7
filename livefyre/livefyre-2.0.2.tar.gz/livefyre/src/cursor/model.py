class CursorData(object):
    def __init__(self, resource, limit, date):
        self.resource = resource
        self.limit = limit
        self.cursor_time = date.utcnow().isoformat() + 'Z' if date else None
        self.hasNext = False
        self.hasPrevious = False

    def set_cursor_time(self, date):
        self.cursor_time = date.utcnow().isoformat() + 'Z' if date else None