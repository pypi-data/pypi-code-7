# -*- coding: utf-8 -*-
'''
TaoBao IP(http://ip.taobao.com) Provider
'''

import requests
from copy import copy

from . import BaseProvider
from ip2locale.utils import get_current_time



class TaoBaoProvider(BaseProvider):

    def __init__(self):
        super(TaoBaoProvider, self).__init__()
        self.ret['source'] = 'taobao'

    @staticmethod
    def get_ip2locale(ip, timeout=5):
        ret = {
            'error': [],
        }
        api_url = 'http://ip.taobao.com/service/getIpInfo.php'
        payload = {'ip': ip}
        try:
            r = requests.get(api_url, params=payload, timeout=timeout)
        except Exception as e:
            ret['error'].append(str(e))
            return ret
        if r.status_code != 200:
            ret['error'].append('status_code(%d) is not 200' %r.status_code)
        else:
            ret.update(r.json())
            for each_key in ret['data']:
                if isinstance(each_key, unicode):
                    ret['data'][each_key.encode('utf-8')] = ret['data'].pop(each_key)
        return ret

    def query(self, ip):
        ret = copy(self.ret)
        result = TaoBaoProvider.get_ip2locale(ip, timeout=self.timeout)
        ret['query_time'] = get_current_time()
        if not result.get('error') and result.get('code') == 0:
            ret['status'] = 0
            ret.update(result['data'])
        return ret








