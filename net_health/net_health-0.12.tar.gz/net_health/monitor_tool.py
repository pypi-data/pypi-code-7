#!/usr/bin/env python
import ast
import subprocess

import logging

from neutronclient.v2_0 import client
from credentials import get_credentials
from credentials import get_nova_credentials_v2
from novaclient.client import Client
from remote_client import RemoteClient
from utils import NovaManageExec

LOG = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
LOG.addHandler(ch)
LOG.setLevel(logging.DEBUG)


def main(src_instance_id):
    return MonitorTool(src_instance_id).get_latency_measurment(src_instance_id)
    #ceilometer statistics -m vcpus -p 60*5

class MonitorTool(object):

    def __init__(self, src_instance_id):
        neutron_credentials = get_credentials()
        self.neutron_client = client.Client(**neutron_credentials)
        nova_credentials = get_nova_credentials_v2()
        self.nova_client = Client(**nova_credentials)
        self.src_vm_instance_id = src_instance_id

    def get_latency_measurment(self):
        netw = self.neutron_client.list_networks(** {'router:external': 'False'})
        netw_ids = [network['id'] for network in netw['networks']]
        src_ip_address = filter(lambda x: x.instance_id ==
                self.src_vm_instance_id,
                self.nova_client.floating_ips.list())[0].ip
        for net_id in netw_ids:
            return [self._get_tenant_network_latency(src_ip_address, vm_port)
                    for vm_port in
                    self.neutron_client.list_ports(
                        network_id=net_id, device_owner="compute:nova")['ports']]

    def _get_host_id(self, instance_id=None):
        ports = self.neutron_client.list_ports(**{'device_id': instance_id})
        host_id = ports['ports'][0]['binding:host_id']
        return host_id

    def _get_tenant_network_latency(self, src_ip, target_vm_port):
        target_ip_address = target_vm_port['fixed_ips'][0]['ip_address']
        LOG.debug('checking internal network connections to IP %s' %
                  target_ip_address)
        try:
            latency_measurement = self._get_ping_time(
                src_ip, target_ip_address)
            if not latency_measurement:
                host_id = target_vm_port['binding:host_id']
                self._check_host_connectivity(host_id)
            return latency_measurement
        except Exception as e:
            LOG.error('Tenant network connectivity check failed: %s' % e)
            raise

    def _get_remote_client(self, dest_ip_address,  username):
        return RemoteClient(dest_ip_address, username)

    def _get_ping_time(self, src_ip_address,
                       target_ip_address, username='ubuntu', num_pings=1):
        #source_vm = self._get_remote_client(src_ip_address, username)

        LOG.debug("try pinging ip: %s" % target_ip_address)
        ping_res = self.ping_host(target_ip_address, num_pings)
        if ping_res:
            LOG.debug("ping success to ip: %s measured %s" %
                      (target_ip_address, ping_res))
        else:
            LOG.error("Timed out waiting for %s to become reachable" %
                      target_ip_address)
        return ping_res

    def _get_host_ip_dict(self):
        nova_manage = NovaManageExec('get_host_ip_nova_manage_script.py')
        return nova_manage.call()[0]

    def _check_host_connectivity(self, host_id):
        host_name_ip_dict = self._get_host_ip_dict()
        src_host_id = self._get_host_id(self.src_vm_instance_id)
        src_host_ip = ast.literal_eval(host_name_ip_dict)[src_host_id]
        host_ip = ast.literal_eval(host_name_ip_dict)[host_id]
        LOG.debug("try pinging host: %s" % host_ip)
        return self._get_ping_time(src_host_ip, host_ip, 'root')


#     not needed anymore - for local ping
#     def _ping_ip_address(self, ip_address):
#         cmd = ['ping', '-c1', '-w1', ip_address]
#         proc = subprocess.Popen(cmd,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE)
#         proc.wait()
#         return proc.returncode == 0
#
    def _check_public_network_connectivity(self,
                                           src_ip_address, target_vm_port):
        floating_ip = filter(lambda x: x.instance_id ==
                             target_vm_port['device_id'],
                             self.nova_client.floating_ips.list())[0].ip
        LOG.debug('checking extenal connections to IP %s' % floating_ip)
        try:
            self._get_ping_time(src_ip_address, floating_ip)
        except Exception as e:
            LOG.error('Public network connectivity check failed: %s' % e)
            raise

    def ping_host(self, host, num_pings=1):
        cmd = "ping -c %d -w %d %s  | tail -1 | awk '{print $4}' | cut -d '/' -f2" % (num_pings, num_pings, host)
        proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        result_code = proc.returncode
        if result_code == 0:
            return out.rstrip()
        return 0
