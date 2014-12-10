from enum import Enum
from livefyre.src.exceptions import LivefyreException
from livefyre.src.utils import pyver


try:
    import simplejson as json
except ImportError:
    import json


class Subscription(object):
    def __init__(self, to, by, sub_type, created_at=None):
        self.to = to
        self.by = by
        self.sub_type = sub_type
        if created_at:
            self.created_at = created_at
        
    @staticmethod
    def serialize_from_json(json_obj):
        try:
            try:
                sub_type = SubscriptionType(json_obj['type'])
            except ValueError:
                sub_type = SubscriptionType[json_obj['type']]
        except Exception:
            raise LivefyreException('A valid type was not passed in.')
        
        return Subscription(json_obj['to'], json_obj['by'], sub_type, json_obj['createdAt'])
    
    def to_dict(self):
        sub_dict = {
            'to': self.to,
            'by': self.by,
            'type': self.sub_type.name,
        }
        
        if hasattr(self, 'created_at'):
            sub_dict['createdAt'] = self.created_at
        return sub_dict
        
    #json hack to get around jwt json dumps
    def _json_support(*args):
        def default(self, o):
            if pyver > 3.0:
                if isinstance(o, bytes):
                    return
            return o.to_dict()
        json.JSONEncoder.default = default
    _json_support()

        
class SubscriptionType(Enum):
    personalStream = 1