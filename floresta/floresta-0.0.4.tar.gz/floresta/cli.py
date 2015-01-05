#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from __future__ import unicode_literals
import re
import os
import sys
import argparse
import logging
from itertools import chain
sys.path.append(os.getcwd())

from floresta.parser import VPCBlueprint
from floresta.core import VPCEngine
from floresta.models import ELASTIC_IPS, DOMAINS, PUBLIC_IPS, FlorestaError
from floresta.log import logger, FlorestaLogHandler
from floresta.version import __version__ as version


parser = argparse.ArgumentParser(
    description='Amazon VPC creation tool')

parser.add_argument(
    'filename',
    type=str,
    help=("YAML file containing the VPC blueprint"),
)

parser.add_argument(
    '-y', '--yes',
    action='store_true',
    default=False,
    help=("don't ask for confirmation"),
)

parser.add_argument(
    '-q', '--quiet',
    action='store_true',
    default=False,
    help=("print logs"),
)

parser.add_argument(
    '--debug',
    action='store_true',
    default=False,
    help=("print logs in debug mode (overwrites the -q option)"),
)

parser.add_argument(
    '--ansible',
    action='store_true',
    default=False,
    help=("runs ansible playbooks in all machines, to specify only some machines use the --machines=<name>,<name2>,... parameter"),
)

parser.add_argument(
    '--list-machines',
    action='store_true',
    default=False,
    help=("just list the machines in the current vpc, even the not-running ones"),
)

parser.add_argument(
    '-m', '--machines',
    action='append',
    help=("a comma-separated list of machine names used by the parameter: --ansible"),
)

parser.add_argument(
    '--no-color',
    action='store_true',
    help=("disable fancy output"),
)

parser.add_argument(
    '--inventory-path',
    help=("the path where the inventory should be placed (also where ansible will look for group_vars and host_vars)"),
)

parser.add_argument(
    '--cache-file-path',
    type=str,
    default=None,
    help=("The path where floresta will store the metadata of the objects created in amazon"),
)

parser.add_argument(
    '--ensure-vpc',
    action='store_true',
    dest='ensure_vpc',
    help=("ensure that the vpc and all of its elements exist"),
)

parser.set_defaults(ensure_vpc=False)

parser.add_argument(
    '--ssh',
    help=("the machine name to ssh to"),
)


def fix_argument(x):
    found = re.search('--([\w-]+)=(.*)', x)
    if not found:
        return x

    return "--{0}='{1}'".format(found.group(1), found.group(2))


def run_cli():
    args, remaining = parser.parse_known_args()

    if args.quiet:
        LOGLEVEL = logging.WARNING
    else:
        LOGLEVEL = logging.INFO

    if args.debug:
        LOGLEVEL = logging.DEBUG

    if args.no_color:
        log_handler = logging.StreamHandler(stream=sys.stderr)
    else:
        log_handler = FlorestaLogHandler(stream=sys.stderr, level=logging.DEBUG)

    logger.setLevel(LOGLEVEL)
    logger.addHandler(log_handler)

    machines = list(chain(*[m.split(',') for m in args.machines or []]))

    blueprint = VPCBlueprint.from_file(args.filename)
    engine = VPCEngine.from_blueprint(blueprint)

    # Validate the given ssh key!
    engine.validate_key(args)

    print "\033[1;37m{1} v{0}\n".format(version, """\033[0;32m
,---.|                        |
|__. |    ,---.,---.,---.,---.|--- ,---.
|    |    |   ||    |---'`---.|    ,---|
`    `---'`---'`    `---'`---'`---'`---^\033[1;37m""")

    vpc_name = engine.blueprint.conf.vpc.name
    cache_file_path = args.cache_file_path or ".cache.{0}.json".format(vpc_name)

    if not args.ssh and not args.list_machines:
        print "{0} tiers".format(len(blueprint.conf.vpc.machines))
        print "{0} machines".format(len(blueprint.conf.vpc.machines))

        if blueprint.conf.vpc.load_balancers:
            print "{0} load balancers".format(len(blueprint.conf.vpc.load_balancers.machines))

        if DOMAINS:
            print "domains to be reset:"
            print

        for machine in blueprint.conf.vpc.machines:
            domain = machine.get('domain', None)
            if not domain:
                continue

            print "\033[1;34m{0}\033[0m".format(domain), 'pointing to ec2 machine\033[1;37m', machine.name, "\033[0m"

        if blueprint.conf.vpc.load_balancers:
            for machine in blueprint.conf.vpc.load_balancers.machines:
                domain = machine.get('domain', None)
                if not domain:
                    continue

                print "\033[1;32m{0}\033[0m".format(domain), 'pointing to load balancer machine\033[1;32m', machine.name, "\033[0m"

        for machine in [blueprint.conf.vpc.jumpbox]:
            domain = machine.get('domain', None)
            if not domain:
                continue

            print "\033[1;33m{0}\033[0m".format(domain), 'pointing to jump box\033[1;33m', machine.name, "\033[0m"

        print

    if args.yes or args.ssh or args.list_machines:
        answer = 'yes'
    else:
        answer = 'VOID'
        print "does that look correct ?"

    while answer not in ['yes', 'no']:
        try:
            answer = raw_input('type "\033[1;32myes\033[0m" or "\033[1;31mno\033[0m"\n').lower().strip()
        except KeyboardInterrupt:
            answer = 'no'

    if answer == 'no':
        print "\r\033[1;33mVPC CREATION Aborted\033[0m\n\r"
        raise SystemExit(2)

    if args.list_machines:
        if not args.ensure_vpc:
            engine.load_stack_from_cache(cache_file_path)
        engine.list_machines(args)
        return

    if args.ssh:
        engine.ssh(args)
        return

    if args.ensure_vpc or not os.path.exists(cache_file_path):
        try:
            engine.create()
        except FlorestaError as e:
            logger.error(e.message)
            return sys.exit(1)

        except KeyboardInterrupt:
            print "\rAborted"
            print
            return sys.exit(1)
    elif not args.ensure_vpc and not os.path.exists(cache_file_path):
            sys.stderr.write('--no-ensure-vpc could find cache file "{0}", you can run floresta again without --no-ensure-vpc to get or create the amazon object and write the cache to a local file'.format(cache_file_path))
            raise SystemExit(1)

    elif not args.ensure_vpc:
        engine.load_stack_from_cache(cache_file_path)

    engine.store_cache(cache_file_path)

    if ELASTIC_IPS or PUBLIC_IPS or DOMAINS:
        print
        print "=" * 70

    for ip, machine in ELASTIC_IPS.items():
        print "\033[1;33mElastic IP: \033[1;37m{0} \033[0massociated with instance \033[1;37m{1}\033[0m".format(ip, machine.name)

    for ip, machine in PUBLIC_IPS.items():
        print "\033[1;34mPublic IP: \033[1;37m{0} \033[0massociated with instance \033[1;37m{1}\033[0m".format(ip, machine.name)

    for domain, machine in DOMAINS.items():
        print "\033[1;32mDOMAIN: \033[1;37m{0} \033[0massociated with instance \033[1;37m{1}\033[0m".format(domain, machine.name)

    if ELASTIC_IPS or PUBLIC_IPS or DOMAINS:
        print "=" * 70
        print

    extra_args = [fix_argument(a) for a in remaining]
    if args.ansible:
        engine.run_ansible_playbooks(extra_args=extra_args, ansible_inventory_path=args.inventory_path, only_machines=machines)


if __name__ == '__main__':
    run_cli()
