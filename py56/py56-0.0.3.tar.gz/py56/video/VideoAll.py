#-*- coding:utf-8 -*-
from py56 import ApiAbstract

class VideoAll(ApiAbstract):
    '''
     Video_All
     @todo get video list from http://video.56.com

     @param $type
     @param $t
     @param $c
     @param $page
     @param $rows

     type:
         hot为最多观看，
         ding为最多推荐，
         new为最新发布，
         share为最多引用，
         comment为最多评论
     t:
         today今日，
         week本周，
         month本月
     c:
         3=>'原创',
         26=>'游戏',
         1=>'娱乐',
         34=>'亲子',
         28=>'汽车',
         27=>'旅游',
         11=>'女性',
         14=>'体育',
         8=>'动漫',
         10=>'科教',
         2=>'资讯',
         39=>'财富',
         40=>'科技',
         41=>'音乐',
         0=>'所有',
         4=>'搞笑',

     @uses ApiAbstract
     @package
     @author Allan Sun <email:alnsun.cn@gmail.com>
    '''

    def get(self, **kwargs):
        '''
        @name Get
        @todo
        @author Allan

        @param string params
        @access public
        @return array
        '''
        url = '%s%s' % (self.domain, '/video/all.json')
        return self.getHttp(url, **kwargs)
