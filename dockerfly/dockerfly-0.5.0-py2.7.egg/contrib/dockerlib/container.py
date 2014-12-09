#!/bin/env python
# -*- coding: utf-8 -*-

import time
import docker as dockerpy
from datetime import datetime

from dockerfly.contrib.network.veth import MacvlanEth
from dockerfly.contrib.dockerlib.libs import run_in_process

class Container(object):

    docker_cli = dockerpy.Client(base_url='unix://var/run/docker.sock')

    @classmethod
    @run_in_process
    def run(cls, image_name, run_cmd, veths, gateway):
        """create basic container, then running

        Args:
            image_name: docker image name
            veths: virtual eths, [('em0v0', 'em0', '192.168.159.10/24'),
                                  ('em1v1', 'em1', '192.168.159.11/24')... )],

                   !!!notify!!!:
                   the first eth will be assigned to the default gateway for container
        Return:
            container_id
        """
        container_name = "dockerfly_%s_%s" % (image_name.replace(':','_').replace('/','_'),
                                              datetime.fromtimestamp(int(time.time())).strftime('%Y%m%d%H%M%S'))
        container = cls.docker_cli.create_container(image=image_name,
                                                    command=run_cmd,
                                                    name=container_name)
        container_id = container.get('Id')

        cls.docker_cli.start(container=container_id, privileged=True)

        for index, (veth, link_to, ip_netmask) in enumerate(veths):
            macvlan_eth = MacvlanEth(veth, ip_netmask, link_to).create()
            container_pid = cls.docker_cli.inspect_container(container_id)['State']['Pid']

            if index == 0:
                macvlan_eth.attach_to_container(container_pid,
                                                is_route=True, gateway=gateway)
            else:
                macvlan_eth.attach_to_container(container_pid)

        return container_id

    @classmethod
    def remove(cls, container_id):
        """remove eths and continer"""
        cls.docker_cli.stop(container_id)
        cls.docker_cli.remove_container(container_id)

    @classmethod
    def get_pid(cls, container_id):
        return cls.docker_cli.inspect_container(container_id)['State']['Pid']

