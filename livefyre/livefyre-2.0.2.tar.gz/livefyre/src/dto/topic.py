from livefyre.src.utils import pyver

try:
    import simplejson as json
except ImportError:
    import json
    

class Topic(object):
    TOPIC_IDENTIFIER = ':topic='
    
    def __init__(self, topic_id, label, created_at=None, modified_at=None):
        self.topic_id = str(topic_id)
        self.label = label
        if created_at:
            self.created_at = created_at
        if modified_at:
            self.modified_at = modified_at
    
    @staticmethod
    def serialize_from_json(json_obj):
        return Topic(json_obj['id'], json_obj['label'], json_obj['createdAt'], json_obj['modifiedAt'])
    
    @staticmethod
    def create(core, topic_id, label):
        return Topic(Topic.generate_urn(core, topic_id), label)
    
    @staticmethod
    def generate_urn(core, topic_id):
        return core.urn + Topic.TOPIC_IDENTIFIER + str(topic_id)
    
    @property
    def truncated_id(self):
        return self.topic_id[self.topic_id.find(self.TOPIC_IDENTIFIER) + len(self.TOPIC_IDENTIFIER):]
    
    def to_dict(self):
        topic_dict = {
            'id': self.topic_id,
            'label': self.label,
        }
        
        if hasattr(self, 'created_at'):
            topic_dict['createdAt'] = self.created_at
        if hasattr(self, 'modified_at'):
            topic_dict['modifiedAt'] = self.modified_at
        return topic_dict
    
    #hack to get around jwt json dumps
    def _json_support(*args):
        def default(self, o):
            if pyver > 3.0:
                if isinstance(o, bytes):
                    return
            return o.to_dict()
        json.JSONEncoder.default = default
    _json_support()
