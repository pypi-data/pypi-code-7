#-*- coding:utf-8 -*-
from py56 import ApiAbstract

class UserApp2Videos(ApiAbstract):

    def get(self, **kwargs):
        '''
        @description 获取当前应用上传视频列表(新)
        @param page->页码，rows->每页显示多少
        @link  /user/app2Videos.json
        @return json
        '''
        url = '%s%s' % (self.domain, '/user/app2Videos.json')
        return self.getHttp(url, **kwargs)
