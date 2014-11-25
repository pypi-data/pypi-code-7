#-*- coding:utf-8 -*-
from py56 import ApiAbstract

class VideoGetVideoInfo(ApiAbstract):
    '''
    Video_GetVideoInfo

    @uses ApiAbstract
    @package
    @author Allan <email:alnsun.cn@gmail.com>
    '''

    def get(self, **kwargs):
        '''
        @description 获取视频信息

          $params=array('vid'=>$flvid);
        @param $flvid 56视频的flvid
        @link /video/getVideoInfo.json
        @return json
        '''
        url = '%s%s' % (self.domain, '/video/getVideoInfo.json')
        return self.getHttp(url, **kwargs)
