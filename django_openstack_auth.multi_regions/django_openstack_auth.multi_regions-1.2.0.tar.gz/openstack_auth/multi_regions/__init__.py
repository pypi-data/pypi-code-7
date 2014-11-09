# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>
import copy

import pbr.version
from django.utils.translation import ugettext_lazy as _


MULTI_REGION_NAMES = {
    'BeiJing-1(PEK-1)': _('BeiJing-1(PEK-1)'),
    'ShenZhen-1(SZX-1)': _('ShenZhen-1(SZX-1)'),
    'Lab-Test-1(Lab-1)': _('Lab-Test-1(Lab-1)'),
    'GuangDong-1(GD-1)': _('GuangDong-1(GD-1)')
}


def i18n(MULTI_REGIONS):
    """i18n for
    ML_REGIONS = [
        ('http://10.0.0.1:5000/v2.0', 'region-1', 'region-name-1'),
        ('http://192.168.1.100:5000/v2.0', 'region-2', 'region-name-2'),
    ]
    """
    _MULTI_REGIONS = [list(i) for i in copy.deepcopy(MULTI_REGIONS)]
    for i in _MULTI_REGIONS:
        i[2] = MULTI_REGION_NAMES.get(i[2], i[2])
    return [tuple(i) for i in _MULTI_REGIONS]


__version__ = pbr.version.VersionInfo(
    'django_openstack_auth.multi_regions').version_string()
