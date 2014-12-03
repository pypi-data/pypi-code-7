from livefyre.src.utils.validator import Validator


class CursorValidator(Validator):
    def validate(self, data):
        reason = ''
        
        reason += self.verify_attr(data, 'resource')
        reason += self.verify_attr(data, 'limit')
        reason += self.verify_attr(data, 'cursor_time')
        
        if len(reason) > 0:
            expl = 'Problems with your cursor input:' + reason
            raise AssertionError(expl)
        
        return data