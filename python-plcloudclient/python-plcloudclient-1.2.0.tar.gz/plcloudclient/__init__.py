# -*- coding: utf-8 -*-
# Copyright 2014 Powerleader, PLCLOUD
# Author: Joe Lei <jiaomin.lei@powerleader.com.cn>

import pbr.version

from plcloudclient import v1_0

__version__ = pbr.version.VersionInfo('python-plcloudclient').version_string()

__all__ = ['v1_0']
