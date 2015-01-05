#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from __future__ import unicode_literals
import re
import json
import time
import boto
import boto.vpc
from boto.exception import BotoServerError
from datetime import datetime
from collections import OrderedDict
from itertools import chain
from boto.route53.exception import DNSServerError
from boto.exception import EC2ResponseError
from boto.ec2.networkinterface import (
    NetworkInterfaceSpecification,
    NetworkInterfaceCollection
)
# from boto.exception import EC2ResponseError
from floresta.log import logger
from floresta.datastructures import DotDict
from floresta.exceptions import FlorestaError


def slugify(string):
    return re.sub(r'\W+', '-', string).lower()


TIERS = {}

JUMPBOX_USERDATA = '''#!/bin/bash

echo "ClientAliveInterval 30" >> /etc/ssh/sshd_config
echo "TCPKeepAlive yes" >> /etc/ssh/sshd_config
echo "ClientAliveCountMax 99999" >> /etc/ssh/sshd_config
echo "MaxStartups 30" >> /etc/ssh/sshd_config
echo "LogLevel VERBOSE" >> /etc/ssh/sshd_config

service sshd restart
'''.strip().encode('base64')

ELASTIC_IPS = OrderedDict()
DOMAINS = OrderedDict()
PUBLIC_IPS = OrderedDict()
MACHINES_BY_NAME = OrderedDict()
LOAD_BALANCERS = OrderedDict()


def get_floresta_playbook_vars():
    return {
        'floresta': {
            'LOAD_BALANCERS': LOAD_BALANCERS,
            'TIERS': TIERS,
            'MACHINES_BY_NAME': dict(MACHINES_BY_NAME),
            'PUBLIC_IPS': dict(PUBLIC_IPS),
            'DOMAINS': dict(DOMAINS),
            'ELASTIC_IPS': dict(ELASTIC_IPS),
        }
    }


class BotoModel(DotDict):
    def __init__(self, data):
        self.update(data)

    @classmethod
    def get_or_create(cls, *args, **kw):
        existing = cls.get_existing(*args, **kw)
        if not existing:
            existing = cls.create(*args, **kw)

        return existing


def tag_boto_object(obj, vpc, name, role=None, tier=None):
    if hasattr(obj, 'update') and callable(obj.update):
        obj.update()

    now = datetime.utcnow()

    obj.add_tag('Name', name)
    obj.add_tag('VPC', vpc.tags['Name'])
    obj.add_tag('LastFlorestaRun', now.isoformat())

    if role:
        obj.add_tag('Role', role)

    if tier:
        obj.add_tag('Tier', tier)


class InstanceProfile(BotoModel):
    def __init__(self, instance_name, vpc_name, tier_name, s3_buckets):
        self.connection = boto.connect_iam()
        self.s3_buckets = s3_buckets
        self.vpc_name = vpc_name
        self.tier_name = tier_name

        self.role_name = '{tier}-{name}-role'.format(
            vpc=vpc_name,
            tier=tier_name,
            name=instance_name,
        )
        self.name = '{tier}-{name}-profile'.format(
            vpc=vpc_name,
            tier=tier_name,
            name=instance_name,
        )

        self.policy_name = '{tier}-{name}-s3-full'.format(
            vpc=vpc_name,
            tier=tier_name,
            name=instance_name,
        )

    def create_profile(self, name):
        try:
            logger.info('creating instance profile %s', name)
            return self.connection.create_instance_profile(name)
        except BotoServerError as e:
            logger.error('{0} [request id: {1}]'.format(e.message, e.request_id))
            return

    def get_existing_profile(self, name):
        try:
            return self.connection.get_instance_profile(name)
        except BotoServerError:
            return

    def get_or_create_profile(self):
        profile = self.get_existing_profile(self.name)
        if not profile:
            profile = self.create_profile(self.name)

        return profile

    def create_role(self, name):
        try:
            logger.info('creating instance role %s', name)
            return self.connection.create_role(name)
        except BotoServerError as e:
            logger.error('{0} [request id: {1}]'.format(e.message, e.request_id))
            return

    def get_existing_role(self, name):
        try:
            return self.connection.get_role(name)
        except BotoServerError:
            return

    def get_or_create_role(self):
        role = self.get_existing_role(self.role_name)
        if not role:
            role = self.create_role(self.role_name)

        return role

    def clear_existing_policies(self, role_name):
        result = self.connection.list_role_policies(role_name)
        response = result['list_role_policies_response']['list_role_policies_result']
        policy_names = response['policy_names']

        for policy_name in policy_names:
            try:
                self.connection.delete_role_policy(role_name, policy_name)
            except BotoServerError as e:
                logger.error('{0} [request id: {1}]'.format(e.message, e.request_id))

    def enable_access_to_buckets(self, buckets):
        self.clear_existing_policies(self.role_name)
        policy = {
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetBucketLocation", "s3:ListAllMyBuckets"],
                    "Resource": "arn:aws:s3:::*"
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": ["arn:aws:s3:::{0}*".format(name) for name in buckets]
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:PutObjectAcl"],
                    "Resource": ["arn:aws:s3:::{0}/*".format(name) for name in buckets]
                }
            ]
        }
        try:
            self.connection.put_role_policy(self.role_name, self.policy_name, json.dumps(policy))
        except BotoServerError as e:
            if 'Cannot exceed quota for InstanceSessionsPerInstanceProfile' not in e.message:
                logger.error('{0} [request id: {1}]'.format(e.message, e.request_id))
                raise FlorestaError('could not put policy {0} to role {1}'.format(policy, self.role_name))

    @classmethod
    def get_or_create(cls, name, vpc_name, tier_name, s3_buckets):
        self = cls(name, vpc_name, tier_name, s3_buckets)

        self.profile = self.get_or_create_profile()
        self.role = self.get_or_create_role()

        try:
            self.bound = self.connection.add_role_to_instance_profile(
                self.name,
                self.role_name,
            )

        except BotoServerError as e:
            if 'Cannot exceed quota for InstanceSessionsPerInstanceProfile' not in e.message:
                logger.error('{0} [request id: {1}]'.format(e.message, e.request_id))
                raise FlorestaError('could not add instance profile {0} to role {1}'.format(self.name, self.role_name))

        self.enable_access_to_buckets(s3_buckets)
        return self


class DNS(BotoModel):
    def __init__(self, hosted_zone_id):
        self.hosted_zone_id = hosted_zone_id
        self.__records = None

    def get_recordset(self):
        conn = boto.connect_route53()
        return conn.get_all_rrsets(self.hosted_zone_id)

    def get_record(self, record_type, domain):
        record_type = record_type.upper()
        matches_type = lambda record: record.type.upper() == record_type.upper()
        matches_domain = lambda record: record.name.lower().rstrip('.') == domain.lower().rstrip('.')

        for record in self.get_recordset():
            if matches_type(record) and matches_domain(record):
                return record

    def delete_existing_record(self, existing):
        recordset = self.get_recordset()
        change = recordset.add_change("DELETE", existing.name, existing.type, ttl=existing.ttl)
        for ex in existing.resource_records:
            change.add_value(ex)

        try:
            recordset.commit()
        except DNSServerError as e:
            logger.error('{0} [request id: {1}]'.format(e.message, e.request_id))

    def delete_record_if_exists(self, record_type, domain):
        record_type = record_type.upper()

        existing = self.get_record(record_type, domain)
        if existing:
            # logger.warning('deleting existing %s record for domain %s', record_type, domain)
            self.delete_existing_record(existing)

    def set_record(self, kind, domain, value):
        domain = "{0}.".format(domain.rstrip('.'))
        kind = kind.upper()

        self.delete_record_if_exists(kind, domain)

        recordset = self.get_recordset()
        logger.info('setting %s record for domain %s with value %s', kind, domain, value)
        change = recordset.add_change("CREATE", domain, kind, ttl='300')
        change.add_value(value)

        try:
            recordset.commit()
        except DNSServerError as e:
            logger.error('{0} [request id: {1}]'.format(e.message, e.request_id))


class Subnet(BotoModel):
    def __init__(self, name, cidr, availability_zone, instance):
        self.name = name
        self.cidr = cidr
        self.availability_zone = availability_zone
        self.instance = instance

    @classmethod
    def get_from_id_list(cls, vpc, subnet_ids):
        raw_subnets = vpc.connection.get_all_subnets(subnet_ids=subnet_ids)

        subnets = [
            cls(
                name=r.tags.get('Name', None),
                cidr=r.cidr_block,
                availability_zone=r.availability_zone,
                instance=r,
            ) for r in raw_subnets]

        return subnets

    @classmethod
    def create(cls, vpc, name, cidr, availability_zone):
        instance = vpc.connection.create_subnet(
            vpc.id,
            cidr,
            availability_zone=availability_zone
        )
        wait_for_subnet(vpc, instance)
        tag_boto_object(instance, vpc, name, role=cls.__name__)
        logger.info('creating new subnet "%s" with cidr_block: %s', instance.id, cidr)

        return cls(name, cidr, availability_zone, instance)

    @classmethod
    def get_existing(cls, vpc, cidr, name, availability_zone):
        subnets = vpc.connection.get_all_subnets(filters={
            'vpcId': [vpc.id],
            'cidrBlock': [cidr]
        })

        if not subnets:
            return

        instance = subnets[0]
        wait_for_subnet(vpc, instance)

        tag_boto_object(instance, vpc, name, role=cls.__name__)

        logger.info(
            'using existing subnet: %s %s',
            instance.id,
            instance.cidr_block
        )
        return cls(
            name,
            cidr,
            instance.availability_zone,
            instance,
        )


class RouteTable(BotoModel):
    def __init__(self, name, subnet, instance, subnets=None):
        self.name = name
        self.subnet = subnet
        self.instance = instance
        self.association = None
        self.subnets = subnets or [subnet]

    def delete_existing_route(self, vpc, cidr_block):
        try:
            vpc.connection.delete_route(self.instance.id, cidr_block)
        except EC2ResponseError as e:
            if 'no route with destination-cidr-block' not in e.message:
                logger.error("{0} [request id: {1}]".format(e.message, e.request_id))

    def set_internet_route(self, vpc, cidr, gateway_id):
        self.delete_existing_route(vpc, cidr)
        try:
            vpc.connection.create_route(self.instance.id, cidr, gateway_id=gateway_id)
            logger.info('setting route %s to gateway %s in route table %s', cidr, gateway_id, self.name)
        except EC2ResponseError as e:
            logger.error("{0} [request id: {1}]".format(e.message, e.request_id))

    def set_instance_route(self, vpc, cidr, instance_id):
        self.delete_existing_route(vpc, cidr)
        try:
            logger.info('setting route %s to instance %s in route table %s', cidr, instance_id, self.name)
            vpc.connection.create_route(self.instance.id, cidr, instance_id=instance_id)
        except EC2ResponseError as e:
            logger.error("{0} [request id: {1}]".format(e.message, e.request_id))

    def associate(self, vpc):
        try:
            self.association = vpc.connection.associate_route_table(self.instance.id, self.subnet.instance.id)

        except Exception:
            logger.warning('ignoring association of route table %s with subnet %s', self.name, self.subnet)

    @classmethod
    def get_main_from_vpc(cls, vpc):
        filters = {
            'association.main': 'true',
            'vpc-id': vpc.id
        }

        main_route_tables = vpc.connection.get_all_route_tables(filters=filters)
        main = main_route_tables[0]
        associated_subnet_ids = filter(bool, [a.subnet_id for a in main.associations])
        subnets = Subnet.get_from_id_list(vpc, associated_subnet_ids)

        name = main.tags.get('Name', 'Main Route Table from {Name}'.format(**vpc.tags))

        return cls(name, None, main, subnets=subnets)

    @classmethod
    def get_existing(cls, vpc, name, subnet):
        found = vpc.connection.get_all_route_tables(filters={
            'vpc-id': vpc.id,
            'association.subnet-id': subnet.instance.id,
        })
        if not found:
            return

        instance = found[0]
        tag_boto_object(instance, vpc, name, role=cls.__name__)

        self = cls(name, subnet, instance)
        self.associate(vpc)

        return self

    @classmethod
    def create(cls, vpc, name, subnet):
        instance = vpc.connection.create_route_table(vpc.id)
        time.sleep(5)
        tag_boto_object(instance, vpc, name, role=cls.__name__)

        self = cls(name, subnet, instance)
        self.associate(vpc)
        logger.info('creating new route table: %s (%s)', name, instance.id)
        return self


class SecurityGroup(BotoModel):
    def __init__(self, name, description, instance):
        self.name = name
        self.description = description
        self.instance = instance
        self.inbound_rules = []
        self.outbound_rules = []

    @classmethod
    def create(cls, vpc, name, description):
        name = slugify(name)
        instance = vpc.connection.create_security_group(name, description, vpc_id=vpc.id)
        tag_boto_object(instance, vpc, name, role=cls.__name__)
        self = cls(name, description, instance)
        return self

    @classmethod
    def get_existing(cls, vpc, name, description):
        name = slugify(name)
        groups = vpc.connection.get_all_security_groups(filters={
            'group-name': name,
            'vpc-id': vpc.id
        })
        if not groups:
            return

        instance = groups[0]
        tag_boto_object(instance, vpc, name, role=cls.__name__)
        self = cls(name, description, instance)
        return self

    def get_existing_inbound_rule(self, from_port, to_port, protocol):
        match_ports = lambda rule: (
            str(rule.from_port) == str(from_port) and
            str(rule.to_port) == str(to_port) and
            rule.ip_protocol.lower() == protocol.lower()
        )
        existing = [r for r in self.instance.rules if match_ports(r)]
        if existing:
            return existing[0]

    def get_existing_outbound_rule(self, from_port, to_port, protocol):
        match_ports = lambda rule: (
            str(rule.from_port) == str(from_port) and
            str(rule.to_port) == str(to_port) and
            rule.ip_protocol.lower() == protocol.lower()
        )

        existing = [r for r in self.instance.rules_egress if match_ports(r)]
        if existing:
            return existing[0]

    def set_inbound_rule(self, vpc, source_cidr, from_port, to_port, protocol='TCP'):
        self.inbound_rules.append({
            'source_cidr': source_cidr,
            'from_port': from_port,
            'to_port': to_port,
        })
        duplicated_entry = self.get_existing_inbound_rule(from_port, to_port, protocol)

        if duplicated_entry:
            logger.debug(
                'ignoring duplicated rule: %s %s',
                duplicated_entry.grants,
                '-'.join([from_port, to_port]),
            )
            return  # abort

        params = dict(
            group_id=self.instance.id,
            ip_protocol=protocol,
            cidr_ip=source_cidr,
            from_port=from_port,
            to_port=to_port
        )
        try:
            success = vpc.connection.authorize_security_group(**params)
            logger.info(
                'authorized inbound traffic from %s (%s) in security group %s: %s',
                source_cidr,
                '-'.join([from_port, to_port]),
                self.instance.id,
                success
            )
        except EC2ResponseError as e:
            logger.error("{0} [request id: {1}]".format(e.message, e.request_id))
            raise FlorestaError(
                'Failed to set inbound rule {}, {}-{}, {} in group {}'.format(
                    source_cidr, from_port, to_port, protocol, self.name))

    def set_outbound_rule(self, vpc, destination_cidr, from_port, to_port, protocol):
        self.outbound_rules.append({
            'destination_cidr': destination_cidr,
            'from_port': from_port,
            'to_port': to_port,
        })

        duplicated_entry = self.get_existing_outbound_rule(from_port, to_port, protocol)

        if duplicated_entry:
            logger.debug(
                'ignoring duplicated rule: %s %s',
                duplicated_entry.grants,
                '-'.join([from_port, to_port]),
            )
            return  # abort

        params = dict(
            group_id=self.instance.id,
            ip_protocol=protocol,
            cidr_ip=destination_cidr,
            from_port=from_port,
            to_port=to_port
        )

        try:
            success = vpc.connection.authorize_security_group_egress(**params)
            logger.info(
                'authorized outbound traffic from %s (%s) in security group %s: %s',
                destination_cidr,
                '-'.join([from_port, to_port]),
                self.instance.id,
                success
            )

        except EC2ResponseError as e:
            logger.error("{0} [request id: {1}]".format(e.message, e.request_id))
            raise FlorestaError(
                'Failed to set outbound rule {}, {}-{}, {} in group {}'.format(
                    destination_cidr, from_port, to_port, protocol, self.name))

    def clear_undeclared_inbound_rules(self, vpc):
        """Removes any inbound rules that were not previously set by set_inbound_rule"""
        for rule_obj in self.instance.rules:
            rule = {
                'from_port': rule_obj.from_port,
                'to_port': rule_obj.to_port,
                'source_cidr': str(rule_obj.grants[0])
            }
            if rule not in self.inbound_rules:
                logger.warning("%s removing undeclared inbound rule %s", self.name, rule)
                try:
                    vpc.connection.revoke_security_group(
                        ip_protocol=rule_obj.ip_protocol,
                        from_port=rule_obj.from_port,
                        to_port=rule_obj.to_port,
                        cidr_ip=rule_obj.grants[0],
                        group_id=self.instance.id,
                    )
                except EC2ResponseError as e:
                    logger.error("{0} [request id: {1}]".format(e.message, e.request_id))

    def clear_undeclared_outbound_rules(self, vpc):
        """Removes any outbound rules that were not previously set by set_outbound_rule"""
        for rule_obj in self.instance.rules_egress:
            rule = {
                'from_port': rule_obj.from_port,
                'to_port': rule_obj.to_port,
                'destination_cidr': str(rule_obj.grants[0])
            }
            if rule not in self.outbound_rules:
                logger.warning("removing undeclared outbound rule %s", rule)
                try:
                    vpc.connection.revoke_security_group_egress(
                        ip_protocol=rule_obj.ip_protocol,
                        from_port=rule_obj.from_port,
                        to_port=rule_obj.to_port,
                        cidr_ip=rule_obj.grants[0],
                        group_id=self.instance.id,
                    )
                except EC2ResponseError as e:
                    logger.error("{0} [request id: {1}]".format(e.message, e.request_id))

    def clear_undeclared_rules(self, vpc):
        self.clear_undeclared_inbound_rules(vpc)
        self.clear_undeclared_outbound_rules(vpc)


class EC2Machine(BotoModel):
    def __init__(self, name, gateway=None, subnet=None, security_group=None, keypair=None, availability_zone=None, hosted_zone_id=None, instance=None, instance_profile=None):
        self.name = name
        self.gateway = gateway
        self.subnet = subnet
        self.security_group = security_group
        self.keypair = keypair
        self.availability_zone = availability_zone
        self.hosted_zone_id = hosted_zone_id
        self.instance = instance
        self.instance_profile = instance_profile

    def get_status(self):
        self.instance.update()
        return {
            'state': self.instance.state,
            'ip_address': self.instance.ip_address,
            'private_ip_address': self.instance.private_ip_address,
        }

    def get_hostname(self):
        return self.instance.private_ip_address

    def set_name_and_domain(self, vpc, name, domain):
        if domain:
            DOMAINS[domain] = self
            dns = DNS(self.hosted_zone_id)
            dns.set_record('A', domain, self.instance.ip_address or self.instance.private_ip_address)

        if self.instance.ip_address:
            PUBLIC_IPS[self.instance.ip_address] = self

        return self

    @classmethod
    def get_by_tags(cls, vpc, tags):
        search = vpc.connection.get_all_reservations
        criteria = {
            'instance-state-name': 'running',
        }
        for k, v in tags.items():
            criteria['tag:{0}'.format(k)] = v

        reservations = search(filters=criteria)
        if not reservations:
            return

        instance = reservations[0].instances[0]
        name = instance.tags['Name']

        self = cls(name, instance=instance)
        return self

    @classmethod
    def get_existing(cls, vpc, name, ami_id, instance_type, gateway,
                     subnet, security_group, keypair, availability_zone, hosted_zone_id,
                     public=False, domain=None, instance_profile=None):

        reservations = vpc.connection.get_all_reservations(filters={
            'image-id': ami_id,
            'instance-state-name': 'running',
            'tag:Name': name
        })
        logger.info('retrieving {0} instance: {1}'.format(instance_type, name))
        if not reservations:
            return

        instance = reservations[0].instances[0]

        self = cls(name, gateway, subnet, security_group, keypair, availability_zone, hosted_zone_id, instance)

        wait_for_instance(vpc, instance)
        self.set_name_and_domain(vpc, name, domain)
        return self

    @classmethod
    def create(cls, vpc, name, ami_id, instance_type, gateway,
               subnet, security_group, keypair, availability_zone, hosted_zone_id,
               public=False, domain=None, instance_profile=None):

        wait_for_subnet(vpc, subnet.instance)

        interface = NetworkInterfaceSpecification(
            subnet_id=subnet.instance.id,
            associate_public_ip_address=public,
            groups=[security_group.instance.id],
        )
        interfaces = NetworkInterfaceCollection(interface)

        if instance_profile:
            instance_profile_name = instance_profile.name
        else:
            instance_profile_name = None

        result = vpc.connection.run_instances(
            ami_id,
            key_name=keypair,
            instance_type=instance_type,
            placement=availability_zone,
            network_interfaces=interfaces,
            instance_profile_name=instance_profile_name,
        )
        logger.info('creating {0} instance: {1}'.format(instance_type, name))
        instance = result.instances[0]

        self = cls(name, gateway, subnet, security_group, keypair, availability_zone, hosted_zone_id, instance)

        wait_for_instance(vpc, instance)
        self.set_name_and_domain(vpc, name, domain)
        return self


class LoadBalancerMachine(DotDict):
    def get_or_create(self, vpc, name, gateway, subnet, security_group, conf):
        ami_id = self['ami-id']
        instance_type = self['instance-type']
        domain = self.get('domain', None)
        keypair = conf.vpc.security.keypair

        ec2_instance = EC2Machine.get_or_create(
            vpc,
            name,
            ami_id,
            instance_type,
            gateway,
            subnet,
            security_group,
            keypair,
            conf.vpc.availability_zone,
            conf.vpc.hosted_zone_id,
            public=True,
            domain=domain,
            instance_profile=None
        )

        self.update(ec2_instance)
        tag_boto_object(ec2_instance.instance, vpc, name, role=self.__class__.__name__)
        LOAD_BALANCERS[name] = self
        return self

    def get_hostname(self):
        return self.instance.ip_address


class LoadBalancerCollection(DotDict):
    def initialize(self):
        self.machines = [LoadBalancerMachine(m) for m in self.machines]

    def get_or_create_security_group(self, vpc, security_group_name, cidr, conf):
        description = 'Load Balancers in the {0}'.format(vpc.tags['Name'])

        security_group = SecurityGroup.get_or_create(
            vpc=vpc,
            name=security_group_name,
            description=description
        )
        # # inbound rules

        # enable ssh inbound from anywhere
        security_group.set_inbound_rule(
            vpc,
            source_cidr=cidr,
            from_port='22',
            to_port='22',
            protocol='TCP',
        )

        # enable http inbound from the local subnet
        security_group.set_inbound_rule(
            vpc,
            source_cidr='0.0.0.0/0',
            from_port='80',
            to_port='80',
            protocol='TCP',
        )

        # enable https inbound from the local subnet
        security_group.set_inbound_rule(
            vpc,
            source_cidr='0.0.0.0/0',
            from_port='443',
            to_port='443',
            protocol='TCP',
        )

        # # outbound rules

        # enable HTTP outbound to anywhere
        security_group.set_outbound_rule(
            vpc,
            destination_cidr='0.0.0.0/0',
            from_port='80',
            to_port='80',
            protocol='TCP',
        )

        # enable HTTPS outbound to anywhere
        security_group.set_outbound_rule(
            vpc,
            destination_cidr='0.0.0.0/0',
            from_port='443',
            to_port='443',
            protocol='TCP',
        )

        security_group.clear_undeclared_rules(vpc)

        return security_group

    def get_or_create(self, vpc, gateway, jumpbox, conf):
        jumpbox_cidr = jumpbox.cidr
        cidr = self.cidr

        subnet_name = '{0}-loadbalancers-subnet'.format(conf.vpc.name)
        route_table_name = '{0}-loadbalancers-rt'.format(conf.vpc.name)
        security_group_name = '{0}-loadbalancers-sg'.format(conf.vpc.name)

        availability_zone = conf.vpc.availability_zone

        # Create subnet
        subnet = Subnet.get_or_create(vpc, name=subnet_name, cidr=cidr, availability_zone=availability_zone)

        # Create route table
        route_table = RouteTable.get_or_create(vpc, route_table_name, subnet)
        route_table.set_internet_route(vpc, "0.0.0.0/0", gateway.id)

        # Create SecurityGroup
        security_group = self.get_or_create_security_group(vpc, security_group_name, jumpbox_cidr, conf)

        for index, machine in enumerate(self.machines, start=1):
            name = machine.name
            machine = machine.get_or_create(vpc, name, gateway, subnet, security_group, conf)

        return self


class JumpBox(DotDict):
    def initialize(self):
        self.associated_elastic_ip = None

    def get_hostname(self):
        return self.associated_elastic_ip or self.instance.ip_address

    def get_elastic_ip(self, vpc):
        elastic_ip = self.get('elastic-ip', None)
        if not elastic_ip:
            return None

        for addr in vpc.connection.get_all_addresses():
            if addr.public_ip == elastic_ip:
                return addr

        logger.error('the given elastic ip: %s does not exist', elastic_ip)

    def get_or_create(self, vpc, gateway, conf):
        ami_id = self['ami-id']
        keypair = conf.vpc.security.keypair

        tier = Tier(self, DotDict({
            'region': conf.vpc.region,
            'availability_zone': conf.vpc.availability_zone,
            'name': '{0}-public'.format(vpc.tags['Name']),
        }))

        self['tier'] = tier.get_or_create(vpc, gateway)

        instance = self.get_or_create_jumpbox(
            vpc,
            ami_id,
            keypair,
            tier.availability_zone,
            tier.subnet.instance.id,
            [tier.security_group.instance.id],
        )

        elastic_ip = self.get_elastic_ip(vpc)
        if elastic_ip:
            elastic_ip.associate(instance.id)
            self.associated_elastic_ip = elastic_ip.public_ip
            ELASTIC_IPS[self.associated_elastic_ip] = self

        # allowing the NAT route table to go out through the internet gateway
        tier.route_table.set_internet_route(vpc, '0.0.0.0/0', gateway.id)

        # authorizing traffic from the NAT instance to the world
        main_route_table = RouteTable.get_main_from_vpc(vpc)
        main_route_table.set_instance_route(vpc, '0.0.0.0/0', instance.id)

        # allowing every subnet CIDR send traffic to the NAT machine
        nat_security_group = tier.security_group

        for other_tier in TIERS.values():
            if other_tier.route_table.association == tier.route_table.association:
                continue

            nat_security_group.set_inbound_rule(
                vpc,
                source_cidr=other_tier.cidr,
                from_port='80',
                to_port='80',
                protocol='TCP',
            )

            nat_security_group.set_inbound_rule(
                vpc,
                source_cidr=other_tier.cidr,
                from_port='443',
                to_port='443',
                protocol='TCP',
            )
            nat_security_group.set_outbound_rule(
                vpc,
                destination_cidr=other_tier.cidr,
                from_port='22',
                to_port='22',
                protocol='TCP',
            )
            other_tier.route_table.set_instance_route(vpc, '0.0.0.0/0', instance.id)

        nat_security_group.clear_undeclared_rules(vpc)

        self.instance = instance
        self.set_domain(instance, conf)
        if 'ansible' in self:
            self.ansible['hosts'] = [self.name]

        return self

    def set_domain(self, instance, conf):
        domain = self.get('domain', None)
        if domain:
            dns = DNS(conf.vpc.hosted_zone_id)
            dns.set_record('A', domain, instance.ip_address or self.instance.private_ip_address)

    def get_or_create_jumpbox(self, vpc, ami_id, keypair, availability_zone, subnet_id, security_group_ids):
        instance = self.get_existing_jumpbox(vpc, ami_id, keypair, availability_zone, subnet_id, security_group_ids)
        if not instance:
            instance = self.create_jumpbox(vpc, ami_id, keypair, availability_zone, subnet_id, security_group_ids)
            logger.info('creating NAT instance {3} {0} with image {1}, key {2}'.format(self.name, ami_id, keypair, self['instance-type']))
        else:
            logger.info('using existing NAT instance {0}'.format(self.name))

        tag_boto_object(instance, vpc, self.name, role='JumpBox')

        wait_for_instance(vpc, instance)

        return instance

    def get_existing_jumpbox(self, vpc, ami_id, keypair, placement, subnet_id, security_group_ids):
        filtered_reservations = vpc.connection.get_all_reservations(filters={
            'image-id': ami_id,
            'instance-state-name': 'running',
            'vpc-id': vpc.id
        })
        nat_instances = list(chain(*[r.instances for r in filtered_reservations]))
        if nat_instances:
            instance = nat_instances[0]
            instance.add_tag('Role', self.__class__.__name__)
            return instance

    def create_jumpbox(self, vpc, ami_id, keypair, placement, subnet_id, security_group_ids):
        interface = NetworkInterfaceSpecification(
            subnet_id=subnet_id,
            associate_public_ip_address=True,
            groups=security_group_ids,
        )
        interfaces = NetworkInterfaceCollection(interface)
        result = vpc.connection.run_instances(
            ami_id,
            key_name=keypair,
            placement=self.tier.availability_zone,
            network_interfaces=interfaces,
            user_data=JUMPBOX_USERDATA
        )
        ec2_instance = result.instances[0]
        vpc.connection.modify_instance_attribute(ec2_instance.id, 'sourceDestCheck', False)
        ec2_instance.add_tag('Role', self.__class__.__name__)
        return ec2_instance


def instance_is_ready(vpc, instance):
    statuses = vpc.connection.get_all_instance_status([instance.id])
    if not statuses:
        return

    st = statuses[0]
    instance_status = st.instance_status
    system_status = st.system_status

    if instance_status.status == 'impaired' or system_status.status == 'impaired' or instance_status.details['reachability'] == 'failed' or system_status.details['reachability'] == 'failed':
        raise FlorestaError('The instance {0} ({1}) is impaired, troubleshoot in the amazon console'.format(
            instance.tags.get('Name', 'unnamed'),
            instance.id
        ))

    return system_status.details['reachability'] == 'passed' and instance_status.details['reachability'] == 'passed' and instance_status.status == 'ok' and system_status.status == 'ok'


def wait_for_instance(vpc, instance):
    logger.info('waiting for instance %s to be running', instance.id)
    time.sleep(5)
    while instance.state == 'pending':
        instance.update()

    while not instance_is_ready(vpc, instance):
        instance.update()

    return True


def get_subnet_by_id(vpc, subnet_id):
    found = vpc.connection.get_all_subnets([subnet_id])

    if found:
        return found[0]
    else:
        return None


def wait_for_subnet(vpc, instance):
    logger.info('waiting for subnet %s to be available', instance.id)
    iid = instance.id
    while instance.state != 'available':
        try:
            instance = get_subnet_by_id(vpc, instance.id)
        except EC2ResponseError:
            continue

        if instance is None:
            raise FlorestaError('the subnet {0} does not exist'.format(iid))

    return True


class Machine(DotDict):
    def initialize(self):
        self.instance_name = "{0} [{1}]".format(self.name, self.tier)
        self.profile = {}
        MACHINES_BY_NAME[self.name] = self

        if 'public' not in self:
            self.public = False

    def get_ip_address(self):
        if self.public:
            return self.instance.ip_address
        return self.instance.private_ip_address

    def get_or_create(self, vpc, gateway, conf):
        if self.tier not in TIERS:
            logger.error('the machine {0} points to an unexisting tier: {1}'.format(self.name, self.tier))
            raise SystemExit(1)

        tier = TIERS[self.tier]
        ami_id = self['ami-id']
        instance_type = self['instance-type']

        authorized_buckets = self.get(
            'authorized_buckets', [])

        if authorized_buckets:
            profile = InstanceProfile.get_or_create(
                name=self.name,
                vpc_name=vpc.tags['Name'],
                tier_name=self.tier,
                s3_buckets=authorized_buckets
            )
        else:
            profile = None

        ec2_instance = EC2Machine.get_or_create(
            vpc,
            self.name,
            ami_id,
            instance_type,
            gateway,
            tier.subnet,
            tier.security_group,
            conf.vpc.security.keypair,
            conf.vpc.availability_zone,
            conf.vpc.hosted_zone_id,
            public=self.get('public', False),
            domain=self.get('domain'),
            instance_profile=profile,
        )

        self.update(ec2_instance)
        tag_boto_object(ec2_instance.instance, vpc, self.name, tier=self.tier, role=self.__class__.__name__)

        self.ansible['hosts'] = [self.name]
        return self


class Tier(DotDict):
    def initialize(self, vpc):
        if 'public' not in self:
            self.public = False

        self['region'] = vpc.region
        self['availability_zone'] = vpc.availability_zone
        self['subnet_name'] = '{0}-subnet'.format(self.name)
        self['route_table_name'] = '{0}-route-table'.format(self.name)
        self['security_group_name'] = '{0}-sg'.format(self.name)

    def get_or_create(self, vpc, gateway):
        self.subnet = Subnet.get_or_create(
            vpc,
            name=self.subnet_name,
            cidr=self.cidr,
            availability_zone=self.availability_zone
        )
        self.route_table = RouteTable.get_or_create(vpc, self.route_table_name, self.subnet)
        self.security_group = self.get_or_create_security_group(vpc)

        tag_boto_object(self.subnet.instance, vpc, self.subnet_name, tier=self.name, role='Subnet')
        tag_boto_object(self.route_table.instance, vpc, self.route_table_name, tier=self.name, role='RouteTable')
        tag_boto_object(self.security_group.instance, vpc, self.name, tier=self.name, role='SecurityGroup')

        if self.public:
            self.route_table.set_internet_route(vpc, "0.0.0.0/0", gateway.id)
            logger.info('Tier %s is public through gateway %s', self.name, gateway.id)

        TIERS[self.name] = self
        return self

    def get_protocol_and_ports(self, rule):
        protocol = rule.protocol.strip().lower()
        if rule.get('port'):
            from_port = to_port = str(rule.port)
        elif rule.get('ports'):
            from_port, to_port = rule.ports.split('-')
        else:
            raise SyntaxError('firewall rules need to contain the "port" or "ports" key. Got {0}'.format(rule))

        return protocol, from_port, to_port

    def get_or_create_security_group(self, vpc):
        name = self.security_group_name
        description = 'Tier {0} security group'.format(self.name)

        group = SecurityGroup.get_or_create(vpc, name, description)

        for rule in self.firewall.inbound:
            protocol, from_port, to_port = self.get_protocol_and_ports(rule)
            group.set_inbound_rule(
                vpc=vpc,
                source_cidr=rule.source,
                from_port=from_port,
                to_port=to_port,
                protocol=protocol
            )

        for rule in self.firewall.outbound:
            protocol, from_port, to_port = self.get_protocol_and_ports(rule)
            group.set_outbound_rule(
                vpc=vpc,
                destination_cidr=rule.destination,
                from_port=from_port,
                to_port=to_port,
                protocol=protocol
            )

        return group


class VPC(BotoModel):
    def __init__(self, dct):
        super(VPC, self).__init__(dct)

        self.machines = [Machine(m) for m in self.machines]

        if 'tiers' not in self:
            raise FlorestaError('Missing the "tiers" declaration in the given yaml file')

        self.tiers = [Tier(t, self) for t in
                      self.tiers]

        if 'jumpbox' in self:
            self.jumpbox = JumpBox(self.jumpbox)
        else:
            self.jumpbox = DotDict({})

        if 'load_balancers' in self:
            self.load_balancers = LoadBalancerCollection(
                self.load_balancers)
        else:
            self.load_balancers = DotDict({})

    @classmethod
    def get_by_name_and_region(cls, name, region):
        connection = boto.vpc.connect_to_region(region)

        vpcs = connection.get_all_vpcs(filters={
            'tag:Name': name
        })
        if not vpcs:
            return

        return vpcs[0]
