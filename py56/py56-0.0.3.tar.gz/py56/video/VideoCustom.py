from py56 import ApiAbstract

class VideoCustom(ApiAbstract):
    '''
    params: sid css rurl ourl
    '''

    def get(self, **kwargs):
        url = '%s%s' % (self.domain, '/video/custom.plugin')
        return '%s?%s' % (url, self.signRequest(**kwargs))
