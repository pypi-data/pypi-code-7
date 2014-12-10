from datetime import datetime
from livefyre.src.cursor import TimelineCursor


class CursorFactory(object):
    @staticmethod
    def get_topic_stream_cursor(core, topic, limit=50, date=datetime.now()):
        resource = topic.topic_id + ":topicStream"
        return TimelineCursor.init(core, resource, limit, date)
    
    @staticmethod
    def get_personal_stream_cursor(network, user, limit=50, date=datetime.now()):
        resource = network.get_urn_for_user(user) +":personalStream"
        return TimelineCursor.init(network, resource, limit, date)