# -*- coding: utf-8 -*-

class BaseProvider(object):
    '''
    Ip2Locale Base Provider class
    '''
    def __init__(self):
        self.ret = {
            'country': '',
            'country_id': '',
            'area': '',
            'area_id': '',
            'region': '',
            'region_id': '',
            'city': '',
            'city_id': '',
            'county': '',
            'county_id': '',
            'isp': '',
            'isp_id': '',
            'source': '',   # Provider source
            'status': 1,   # Status: 0 is OK, 1 is Failed
            'query_time': '',
        }
        self.timeout = 5