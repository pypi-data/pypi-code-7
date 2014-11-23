class BeansException(Exception):
    code = ''
    message = ''

    def __init__(self, error):
        if 'code' in error:
            self.code = error['code']

        if 'message' in error:
            self.message = error['message']

        Exception.__init__(self, self.message)