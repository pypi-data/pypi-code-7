# -*- coding:utf-8 -*-
import time
import StringIO

from urllib import urlencode
from hashlib import md5

import pycurl

try:
    from local_config import *
except:
    from config import *

class ApiAbstract(object):
    '''
    author: Allan Sun <email: alnsun.cn@gmail.com;QQ:301585>
    '''

    def __init__(self, **kwargs):

        if not kwargs:
            if APPKEY and SECRET:
                self.appkey = APPKEY
                self.secret = SECRET
            else:
                print 'Please config APPKEY and SECRET in config.py'
                return
            self.domain = DOMAIN

        self.setConf(**kwargs)

        self.CONNECT_TIMEOUT = 5
        self.READ_TIMEOUT = 5


    def setConf(self, **kwargs):

        if not 'appkey' in kwargs or not 'secret' in kwargs:
            print 'APPKEY and SECRET are requiremnets'
            return
        self.appkey = kwargs['appkey']
        self.secret = kwargs['secret']

        if 'domain' in kwargs:
            self.domain = kwargs['domain']
        elif DOMAIN:
            self.domain = DOMAIN

    def getHttp(self, url, **params):
        '''
         @description GET 方法

         @access private
         @param mixed url
         @param dict params
         @return json
        '''
        url = '%s?%s' % (url, self.signRequest(**params)) #$url.'?'.self::signRequest($params);
        print 'url=', url
        return self.httpCall(url) #self::httpCall($url);

    def httpCall(self, url ,params='', method='get', connectTimeout=5, readTimeout=5):
        '''
        @description  curl method,post方法params字符串的位置不同于get

        @access public
        @param mixed url
        @param string params
        @param string method
        @param mixed connectTimeout
        @param mixed readTimeout
        @return json
        '''

        #if self.conf.has_key('print_request_params'):
        #    print 'url:', url, 'params:',params

        result = ""

        timeout = connectTimeout + readTimeout
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        if method.lower() == 'post':
            c.setopt(pycurl.POST, 1)
            c.setope(pycurl.POSTFIELDS, params)
        c.setopt(pycurl.CONNECTTIMEOUT, connectTimeout)
        c.setopt(pycurl.TIMEOUT, timeout)
        #c.setopt(pycurl.RETURNTRANSFER, 1)
        c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:33.0) Gecko/20100101 Firefox/33.0')

        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)

        try:
            result = c.perform()
            return b.getvalue()#result
        except Exception, e:
            print 'Connection error:' + str(e)
            c.close()

    def signRequest(self, **kwargs):

        kv_list = kwargs.items()
        kv_list.sort()

        req = md5(urlencode(kv_list)).hexdigest()
        ts = int(time.time())

        kwargs['appkey'] = self.appkey
        kwargs['sign'] = md5('#'.join([req, self.appkey, self.secret, str(ts)])).hexdigest()
        kwargs['ts'] = str(ts)
        return urlencode(kwargs)
