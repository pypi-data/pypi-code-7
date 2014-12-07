#!/bin/env python
# -*- coding: utf-8 -*-

"""dockerfly bin tool

Usage:
  dockerfly.py ps
  dockerfly.py gen      <config_json>
  dockerfly.py run      <config_json>
  dockerfly.py kill     <config_json>
  dockerfly.py get      <container_id>

Options:
  -h --help             Show this screen.
  --version             Show version.

Example:
    show all containers             python2.7 dockerfly.py ps
    generate container config       python2.7 dockerfly.py gen centos6.json
    start container                 python2.7 dockerfly.py run centos6.json
    remove container                python2.7 dockerfly.py kill e5d898c10bff
    getpid container pid            python2.7 dockerfly.py getpid e5d898c10bff
"""

import os
import sys
import json
from sh import docker, nsenter
from docopt import docopt
import docker as dockerpy

here = os.path.abspath(os.path.dirname(__file__))
try:
    import dockerfly
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(here, '../../')))

dockerfly_version = open(os.path.join(here, '../version.txt')).read().strip()

from dockerfly.contrib.dockerlib.container import Container

def main():
    arguments = docopt(__doc__, version=dockerfly_version)
    docker_cli = dockerpy.Client(base_url='unix://var/run/docker.sock')

    container_json_exp = [{
            'image_name':'centos:centos6',
            'run_cmd': '/bin/sleep 300',
            'eths':
            [
               ('testDockerflyv0', 'eth0', '192.168.159.10/24'),
               ('testDockerflyv1', 'eth0', '192.168.159.11/24'),
            ],
            'gateway':'192.168.159.2'
        }]

    if arguments['ps']:
        print docker('ps')

    if arguments['gen']:
        with open(arguments['<config_json>'], 'w') as config:
            json.dump(container_json_exp, config, indent=4, encoding='utf-8')

    if arguments['run']:
        with open(arguments['<config_json>'], 'r') as config:
            container_json = json.load(config, encoding='utf-8')
            for container in container_json:
                container_id = Container.run(container['image_name'],
                                             container['run_cmd'],
                                             container['eths'],
                                             container['gateway']
                                        )
                print "Container running:ContainerId(%s) Pid(%s)" %(container_id,
                                 docker_cli.inspect_container(container_id)['State']['Pid']
                        )

    if arguments['kill']:
        Container.remove(arguments['<container_id>'])

    if arguments['get']:
        print docker_cli.inspect_container(arguments['<container_id>'])['State']['Pid']

if __name__ == '__main__':
    main()
