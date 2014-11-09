#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals
import re
import yaml
import json

from boto.ec2.ec2object import EC2Object
from boto.ec2.instance import Instance
from boto.ec2.securitygroup import SecurityGroup
from boto.vpc.subnet import Subnet
from boto.vpc.vpc import VPC
from boto.regioninfo import RegionInfo
from boto.vpc.routetable import RouteTable
from boto.vpc.internetgateway import InternetGateway


def yamlify(data):
    ret = yaml.dump(data, default_flow_style=False, allow_unicode=True, encoding='utf-8')
    new = re.sub(r"!!python/\w+ '([^']+)'", '\g<1>', ret)
    return new.decode('utf-8')


class BotoEncoder(json.JSONEncoder):
    def default(self, obj):
        data = {}

        if isinstance(obj, EC2Object):
            if 'Name' in obj.tags:
                data['name'] = obj.tags['Name']

            data['id'] = obj.id
            data['class'] = ".".join([obj.__class__.__module__, obj.__class__.__name__])
            data['tags'] = obj.tags

        if isinstance(obj, Instance):
            data['ip_address'] = obj.ip_address
            data['private_ip_address'] = obj.private_ip_address
        elif isinstance(obj, Subnet):
            data['cidr_block'] = obj.cidr_block
            data['region'] = obj.region
            data['availability_zone'] = obj.availability_zone
        elif isinstance(obj, RegionInfo):
            data['name'] = obj.name

        elif isinstance(obj, RouteTable):
            data['routes'] = [{
                'gateway_id': r.gateway_id,
                'destination': r.destination_cidr_block,
                'state': r.state,
                'instance_id': r.instance_id,
            } for r in obj.routes]
        elif isinstance(obj, SecurityGroup):
            data['description'] = obj.description
        elif isinstance(obj, InternetGateway):
            data['attachments'] = [{'vpc_id': a.vpc_id, 'state': a.state} for a in obj.attachments]
        elif isinstance(obj, VPC):
            data['dhcp_options_id'] = obj.dhcp_options_id
            data['cidr_block'] = obj.cidr_block
            data['state'] = obj.state
            data['instance_tenancy'] = obj.instance_tenancy

        if data:
            return data

        return json.JSONEncoder.default(self, obj)


class DotDict(dict):
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            return super(DotDict, self).__getattribute__(attr)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct=dict(), *args, **kw):
        if not isinstance(dct, dict):
            return

        for key, value in dct.items():
            if hasattr(value, 'keys') and callable(value.keys):
                value = DotDict(value)

            elif isinstance(value, list):
                value = [isinstance(x, dict) and DotDict(x) or x for x in value]

            self[key] = value

        self.initialize(*args, **kw)

    def __setitem__(self, key, value):
        if hasattr(value, 'keys') and callable(value.keys):
            value = DotDict(value)
        elif isinstance(value, list):
            value = [isinstance(x, dict) and DotDict(x) or x for x in value]

        return super(DotDict, self).__setitem__(key, value)

    @classmethod
    def from_yaml(cls, string):
        deserialized = yaml.load(string)
        return cls(deserialized)

    def initialize(self, *args, **kw):
        pass

    def to_json(self, indent=2):
        return json.dumps(self, indent=indent, cls=BotoEncoder).decode('utf-8')

    def to_vanilla_dict(self):
        loaded = json.loads(self.to_json())
        return loaded

    def to_yaml(self, indent=2):
        loaded = self.to_vanilla_dict()
        return yamlify(loaded)

    def to_yaml_list(self, indent=2):
        loaded = self.to_vanilla_dict()
        return yamlify([loaded])

    def __repr__(self):
        this = super(DotDict, self).__repr__()
        classname = self.__class__.__name__
        this = '{0}({1})'.format(classname, this)
        return this
