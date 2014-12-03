from livefyre.src.utils.validator import Validator


class SiteValidator(Validator):
    def validate(self, data):
        reason = ''
        
        reason += self.verify_attr(data, 'id')
        reason += self.verify_attr(data, 'key')
        
        if len(reason) > 0:
            expl = 'Problems with your site input:' + reason
            raise AssertionError(expl)
        
        return data