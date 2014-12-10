from livefyre.src.utils import is_valid_full_url
from .type import CollectionType
from livefyre.src.utils.validator import Validator


class CollectionValidator(Validator):
    def validate(self, data):
        reason = ''
        
        reason += self.verify_attr(data, 'article_id')
        if not hasattr(data, 'type') or not data.type:
            reason += '\n type is missing.'
        elif not isinstance(data.type, CollectionType):
            reason += '\n type must be a CollectionType.'
            
        if not hasattr(data, 'url') or not data.url:
            reason += '\n url is missing.'
        elif not is_valid_full_url(data.url):
            reason += '\n url must be a full domain. ie. http://livefyre.com'
            
        if not hasattr(data, 'title') or not data.title:
            reason += '\n title is missing.'
        elif len(data.title) > 255:
            reason += '\n title\'s length should be under 255 char.'
        
        if len(reason) > 0:
            expl = 'Problems with your collection input:' + reason
            raise AssertionError(expl)
        
        return data