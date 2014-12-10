class Validator(object):
    def verify_attr(self, data, name):
        if not hasattr(data, name) or not getattr(data, name):
            return '\n {} is missing.'.format(name)
        return ''
