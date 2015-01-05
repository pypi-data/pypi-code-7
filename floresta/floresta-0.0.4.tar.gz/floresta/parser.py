#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals
import io
from floresta.datastructures import DotDict
from floresta.models import (
    VPC,
)


class VPCBlueprint(object):
    def __init__(self, raw_yaml):
        self.raw_yaml = raw_yaml
        self.conf = self.get_conf()

    def get_conf(self):
        conf = DotDict.from_yaml(self.raw_yaml)
        conf.vpc = VPC(conf.vpc)
        return conf

    @classmethod
    def from_file(cls, filename):
        with io.open(filename) as fd:
            raw_yaml = fd.read()

        return cls(raw_yaml)
