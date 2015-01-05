#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals

import io
import json
import os
import sys
import time
import stat
import codecs
import subprocess

from boto import vpc
from prettytable import PrettyTable
from floresta.log import logger
from floresta.datastructures import DotDict, yamlify
from floresta.models import get_floresta_playbook_vars, JumpBox, Tier, LoadBalancerCollection, Machine
from itertools import chain

SSH_ARGS = "-o ConnectTimeout=30 -o ControlPath='~/.ssh/mux-%r@%h:%p' -o ForwardAgent=yes -o TCPKeepAlive=yes -o StrictHostKeyChecking=no -o ControlPersist=8h -o ControlMaster=auto -o ProxyCommand='ssh -o TCPKeepAlive=yes -o BatchMode=yes -o StrictHostKeyChecking=no -vvv -A {jumpbox_username}@{jumpbox_ipaddress} nc %h %p'"

PUBLIC_SSH_ARGS = "-o ControlPath='~/.ssh/mux-%r@%h:%p' -o ForwardAgent=yes -o TCPKeepAlive=yes -o StrictHostKeyChecking=no -o ControlPersist=8h -o ControlMaster=auto"


class Stack(DotDict):
    def initialize(self, vpc):
        if 'jumpbox' in self and self.jumpbox:
            self.jumpbox = JumpBox(self.jumpbox)

        if 'tiers' in self and self.tiers:
            self.tiers = [Tier(t, vpc) for t in self.tiers]

        if 'load_balancers' in self and self.load_balancers:
            self.load_balancers = LoadBalancerCollection(self.load_balancers)

        self.machines = [Machine(m) for m in self.machines]


class VPCEngine(object):
    def __init__(self, blueprint):
        self.blueprint = blueprint
        self.region = blueprint.conf.vpc.region
        self.availability_zone = blueprint.conf.vpc.availability_zone

        self._connection = None
        self.stack = DotDict()

    @property
    def connection(self):
        if not self._connection:
            self._connection = vpc.connect_to_region(self.region)

        return self._connection

    def validate_key(self, args):
        conf = self.blueprint.conf
        if 'security' in conf.vpc:
            if 'private_key_location' in conf.vpc.security:
                private_key_location = os.path.expanduser(conf.vpc.security.private_key_location)
                if not os.path.exists(private_key_location):
                    logger.error('given key does not exist: %s', private_key_location)
            else:
                logger.error('missing private_key_location in vpc.security: %s', args.filename)
        else:
            logger.error('missing security.private_key_location in the vpc configuration: %s', args.filename)

    def create(self):
        conf = self.blueprint.conf
        vpc = self.stack.vpc = self.get_or_create_vpc(conf)

        self.stack.gateway = gateway = self.get_or_create_gateway(vpc, conf)
        self.stack.tiers = self.get_or_create_tiers(vpc, gateway, conf)
        self.stack.jumpbox = jumpbox = self.get_or_create_jumpbox(vpc, gateway, conf)
        self.stack.machines = self.get_or_create_machines(vpc, gateway, conf)
        self.stack.load_balancers = self.get_or_create_load_balancers(vpc, jumpbox, gateway, conf)

        self.inventory, self.playbooks = self.craft_inventory(conf)

    def store_cache(self, json_path):
        serialized = self.stack.to_json()
        with codecs.open(json_path, 'w', 'utf-8') as fd:
            fd.write(serialized)

    def load_stack_from_cache(self, path):
        if not os.path.exists(path):
            return

        with codecs.open(path, 'r', 'utf-8') as fd:
            deserialized = json.load(fd)

        self.stack = Stack(deserialized, self.blueprint.conf.vpc)

        conf = self.blueprint.conf
        self.inventory, self.playbooks = self.craft_inventory(conf)

    def ssh(self, args):
        machine_name = args.ssh

        reservations = self.connection.get_all_reservations(filters={
            'tag:Name': machine_name,
            'instance-state-name': 'running',
        })

        if not reservations:
            logger.error('machine not found, try running')
            print "try running:"
            print "floresta {0} --list-machines to see what machines are running and try again".format(args.filename)
            return sys.exit(1)

        instance = reservations[0].instances[0]
        jumpbox_result = self.connection.get_all_reservations(filters={
            'vpc-id': instance.vpc_id,
            'tag:Role': 'JumpBox'
        })

        ssh_key_location = self.blueprint.conf.vpc.security.private_key_location

        if not jumpbox_result and not instance.ip_address:
            logger.error("the given machine name is in a vpc that does not contain a JumpBox")
            return sys.exit(1)
        elif not jumpbox_result and instance.ip_address:
            ssh_command_line = 'ssh -i {0} -A -tt ubuntu@{1}'.format(ssh_key_location, instance.ip_address)
        else:
            jumpbox = jumpbox_result[0].instances[0]
            ssh_command_line = 'ssh -i {2} -A -tt ec2-user@{0} ssh -A -tt ubuntu@{1}'.format(
                jumpbox.ip_address, instance.private_ip_address, ssh_key_location)

        print ssh_command_line
        os.system(ssh_command_line)

    def list_machines(self, args):
        vpc_name = self.blueprint.conf.vpc.name
        if not self.stack:
            vpcs = self.connection.get_all_vpcs(filters={
                'tag:Name': vpc_name
            })

            if not vpcs:
                logger.error('no vpcs found with the name: %s, check the yaml file %s', vpc_name, args.filename)
                sys.exit(1)
                return

            vpc = vpcs[0]
            all_instances = list(chain(*[r.instances for r in self.connection.get_all_reservations(filters={
                'vpc-id': vpc.id,
            })]))
        else:
            all_instances = []

            if 'jumpbox' in self.stack and self.stack.jumpbox:
                all_instances.append(self.stack.jumpbox.instance)

            all_instances.extend([m.instance for m in self.stack.machines])
            if 'load_balancers' in self.stack and self.stack.load_balancers:
                all_instances.extend([m.instance for m in self.stack.load_balancers.machines])

        table = PrettyTable(["Name", "Role", "ip_address", "private_ip_address"])
        table.align = 'l'

        NOT_SET = '\033[1;31mnot set\033[0m'

        ssh_args = []
        for machine in all_instances:
            name = machine.tags.get('Name', None)
            role = machine.tags.get('Role', NOT_SET)
            table.add_row([
                name or NOT_SET,
                role,
                machine.ip_address,
                machine.private_ip_address,
            ])
            if name and role != 'JumpBox':
                ssh_args.append('floresta {0} --ssh={1}'.format(args.filename, name))

        print table
        print
        print "SSH into a machine with"
        print "\n".join(ssh_args)

    def run_ansible_playbooks(self, extra_args, ansible_inventory_path, only_machines):
        conf = self.blueprint.conf
        inventory = self.inventory
        playbooks = self.playbooks
        private_key_path = conf.vpc.security.private_key_location
        inventory_path = '{inventory_path}/{vpc_name}.py'.format(
            vpc_name=conf.vpc.name,
            inventory_path=ansible_inventory_path,
        )

        playbook_path = '{0}.yml'.format(conf.vpc.name)

        self.write_ansible_inventory(inventory_path, inventory)
        self.write_ansible_playbook(playbook_path, playbooks, only_machines)

        logger.info("saved %s and %s", inventory_path, playbook_path)

        cmd = "ansible-playbook -c ssh -i {inventory_path} --private-key={private_key_path} {playbook_path} {extra_args}".format(
            inventory_path=inventory_path,
            private_key_path=private_key_path,
            playbook_path=playbook_path,
            extra_args=' '.join(extra_args),
        )
        logger.info("running ansible")
        logger.info("\033[1;32m%s\033[0m", cmd)

        # automatically adding the ssh key to the running agent
        subprocess.call("/usr/bin/env ssh-add {0}".format(private_key_path), shell=True)
        try:
            subprocess.call(cmd, shell=True)
        except KeyboardInterrupt:  # pragma: no cover
            sys.stderr.write('\r\033[0m\n\rAnsible canceled\n\nto try again:\n{0}\n'.format(cmd))

    def write_ansible_inventory(self, path, inventory):
        with io.open(path, 'w') as fd:
            fd.write('#!/usr/bin/env python\n')
            fd.write('# -*- coding: utf-8 -*-\n\n\n')
            fd.write("print '''{0}'''".format(inventory.to_json()))

        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)

    def write_ansible_playbook(self, path, playbooks, only_machines):
        if not only_machines:
            filtered_playbooks = playbooks
        else:
            filtered_playbooks = []

        for p in playbooks:
            if p['name'] in only_machines:
                filtered_playbooks.append(p)

        with io.open(path, 'w') as fd:
            fd.write('---\n')
            fd.write(yamlify(filtered_playbooks))

    def craft_inventory(self, conf):
        inventory = DotDict({})

        for tier in self.stack.tiers:
            inventory[tier.name] = {
                "hosts": [],
                "children": [],
                "vars": {
                }
            }

        ansible_groups = conf.vpc.get('ansible_groups', {})
        for group, children in ansible_groups.items():
            group_vars = {}
            inventory[group] = {
                'children': children,
                'vars': group_vars
            }

        if self.stack.jumpbox:
            ssh_args = SSH_ARGS.format(
                jumpbox_username=self.stack.jumpbox.user,
                jumpbox_ipaddress=self.stack.jumpbox.get_hostname(),
            )
        else:
            ssh_args = PUBLIC_SSH_ARGS

        os.environ['ANSIBLE_SSH_ARGS'] = ssh_args

        playbook_dicts = []

        load_balancer_children_machines = {}

        if self.stack.jumpbox and 'ansible' in self.stack.jumpbox:
            machine = self.stack.jumpbox
            machine.ansible.hosts = [machine.instance.private_ip_address]
            machine.ansible.name = machine.name
            playbook_dicts.append(machine.ansible.to_vanilla_dict())
            inventory[machine.name] = {
                'hosts': [machine.instance.private_ip_address],
                'vars': {
                    'floresta': {
                        'machine': machine.to_vanilla_dict()
                    }
                }
            }

        for machine in self.stack.machines:
            inventory[machine.name] = {
                'hosts': [machine.get_ip_address()],
                'vars': {
                    'machine': machine
                }
            }

            if machine.tier not in load_balancer_children_machines:
                load_balancer_children_machines[machine.tier] = []

            load_balancer_children_machines[machine.tier].append({
                'private_ip_address': machine.instance.private_ip_address,
                'name': machine.name,
            })

            inventory[machine.tier]['hosts'].append(machine.get_ip_address())
            inventory[machine.tier]['children'].append(machine.get_ip_address())
            group_vars = get_floresta_playbook_vars()
            group_vars['floresta']['machine'] = machine.to_vanilla_dict()

            inventory[machine.tier]['vars'] = group_vars

            machine.ansible.hosts = [machine.get_ip_address()]
            machine.ansible.name = machine.name
            playbook_dicts.append(machine.ansible.to_vanilla_dict())

        load_balancer_tier_name = "{0}-load-balancers".format(conf.vpc.name)
        inventory[load_balancer_tier_name] = DotDict({
            'hosts': [],
            'children': [],
            'vars': {}
        })
        if self.stack.load_balancers:
            for machine in self.stack.load_balancers.machines:
                machine.ansible.hosts = [machine.instance.private_ip_address]
                machine.ansible.name = machine.name
                playbook_dicts.append(machine.ansible.to_vanilla_dict())

                group_vars = {
                    'machines': load_balancer_children_machines,
                    'load_balancer_public_ip': machine.get_hostname()
                }
                group_vars.update(get_floresta_playbook_vars())
                group_vars['floresta']['machine'] = machine.to_vanilla_dict()

                inventory[machine.name] = {
                    'hosts': [machine.instance.private_ip_address],
                    'vars': group_vars,
                }

                inventory[load_balancer_tier_name]['hosts'].append(machine.instance.private_ip_address)
                inventory[load_balancer_tier_name]['children'].append(machine.instance.private_ip_address)
                inventory[load_balancer_tier_name]['vars'] = group_vars

        return inventory, playbook_dicts

    def get_or_create_machines(self, vpc, gateway, conf):
        machines = [t.get_or_create(vpc, gateway, conf) for t in conf.vpc.machines]
        return machines

    def get_or_create_load_balancers(self, vpc, jumpbox, gateway, conf):
        if not conf.vpc.load_balancers:
            return

        load_balancers = conf.vpc.load_balancers.get_or_create(vpc, gateway, jumpbox, conf)
        return load_balancers

    def get_or_create_tiers(self, vpc, gateway, conf):
        tiers = [t.get_or_create(vpc, gateway) for t in conf.vpc.tiers]
        return tiers

    def get_or_create_jumpbox(self, vpc, gateway, conf):
        if not conf.vpc.jumpbox:
            return

        jumpbox = conf.vpc.jumpbox.get_or_create(vpc, gateway, conf)
        return jumpbox

    def get_or_create_gateway(self, vpc, conf):  # pragma: no cover
        gw = self.get_existing_gateway(vpc)
        if gw is None:
            gw = self.create_gateway(vpc)

        gw.add_tag('Name', "{0}-gateway".format(conf['vpc']['name']))
        is_attached = [x for x in gw.attachments if x.vpc_id == vpc.id]
        if not is_attached:
            vpc.connection.attach_internet_gateway(gw.id, vpc.id)

        return gw

    def get_existing_gateway(self, vpc):
        gateways = vpc.connection.get_all_internet_gateways(filters={'attachment.vpc-id': vpc.id})

        if gateways:
            gw = gateways[0]
            logger.debug('using existing gateway for vpc: %s %s', vpc.tags['Name'], vpc.id)
            return gw

    def create_gateway(self, vpc):
        logger.info('creating gateway %s for vpc', vpc.tags['Name'])
        gw = vpc.connection.create_internet_gateway()
        logger.info('attached gateway %s to vpc', gw.id)
        return gw

    def get_or_create_vpc(self, conf):
        vpc = self.get_existing_vpc(conf.vpc.cidr)
        if vpc is None:
            vpc = self.create_vpc(conf.vpc.cidr)
            time.sleep(5)

        vpc.add_tag('Name', conf.vpc.name)

        while vpc.state == 'pending':
            vpc.update()

        vpc.connection.modify_vpc_attribute(vpc.id, enable_dns_support=True)
        vpc.connection.modify_vpc_attribute(vpc.id, enable_dns_hostnames=True)
        return vpc

    def get_existing_vpc(self, cidr_block):  # pragma: no cover
        found = self.connection.get_all_vpcs(filters={'cidrBlock': [cidr_block]})

        if found:
            vpc = found[0]
            logger.info('using existing vpc: %s (%s) %s', vpc.tags.get('Name', 'unnamed'), vpc.id, vpc.cidr_block)
            return vpc

    def create_vpc(self, cidr_block):
        logger.info('creating new vpc with cidr_block: %s', cidr_block)
        return self.connection.create_vpc(cidr_block)

    @classmethod
    def from_blueprint(cls, blueprint):
        return cls(blueprint)
