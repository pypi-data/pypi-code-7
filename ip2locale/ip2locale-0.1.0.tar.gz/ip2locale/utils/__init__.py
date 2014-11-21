# -*- coding: utf-8 -*-

import time
import re

def get_current_time(time_format='%Y%m%d%H%M%S'):
    return time.strftime(time_format)


def is_ip(ip):
    ip_format = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    if ip_format.match(ip):
        return True
    else:
        return False