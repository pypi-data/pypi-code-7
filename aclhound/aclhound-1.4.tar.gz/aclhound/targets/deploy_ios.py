#!/usr/bin/env python2.7
# Copyright (C) 2014 Job Snijders <job@instituut.net>
#
# This file is part of ACLHound
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Upload ACLs to Cisco IOS devices

The following process is followed to ensure zero impact

    upload new ACL with LOCKSTEP- prefix
    replace old ACL with LOCKSTEP-acl on all interfaces with old ACL
    upload new ACL without LOCKSTEP-prefix
    replace LOCKSTEP-acl with new ACL on all interfaces with LOCKSTEP-acl
    remove LOCKSTEP ACL from device

"""

from Exscript.util.interact import read_login
from Exscript.protocols import Telnet, Account

import netrc

from pprint import pprint
from aclhound import textfsm
from StringIO import StringIO


def deploy(hostname=None, acls=None):
    """
    Deploy code in a safe way o a Cisco IOS device.
    """

    try:
        username, enable_pass, password = \
            netrc.netrc().authenticators(hostname)
        account = Account(name=username, password=password,
                          password2=enable_pass)
    except:
        account = read_login()

    def s(conn, line):
        print("   %s" % line)
        conn.execute(line)

    def collect_interfaces(conn):
        template = """# textfsm
Value Required Interface ([^ ]+)
Value Inbound (.*)
Value Outbound (.*)

Start
  ^${Interface} is up
  ^  Outgoing access list is ${Outbound}
  ^  Inbound  access list is ${Inbound} -> Record Start

"""
        template_file = StringIO(template)
        table = textfsm.TextFSM(template_file)
        s(conn, 'show ip int | inc ine pro|list is')
        interface_acl_v4 = table.ParseText(conn.response)

        template = """# textfsm
Value Required Interface ([^ ]+)
Value Inbound (.*)
Value Outbound (.*)

Start
  ^${Interface} is up
  ^  Inbound access list ${Inbound}
  ^  Outgoing access list ${Outbound} -> Record Start

"""
        template_file = StringIO(template)
        table = textfsm.TextFSM(template_file)
        s(conn, 'show ipv6 int  | i ine pro|access list')
        interface_acl_v6 = table.ParseText(conn.response)
        template = """# textfsm
Value Required Vty (\d+\s\d+)
Value Inbound4 ([^ ]+)
Value Outbound4 ([^ ]+)
Value Inbound6 ([^ ]+)
Value Outbound6 ([^ ]+)

Start
  ^line vty ${Vty}
  ^ access-class ${Inbound4} in
  ^ access-class ${Outbound4} out
  ^ ipv6 access-class ${Inbound6} in
  ^ ipv6 access-class ${Outbound6} out -> Record Start

"""
        template_file = StringIO(template)
        table = textfsm.TextFSM(template_file)
        s(conn, 'show run | section line vty')
        interface_acl_vty = table.ParseText(conn.response)

        results = {4: interface_acl_v4, 6: interface_acl_v6}
        # add vty lines
        for vty in interface_acl_vty:
            # v4 inbound
            v4_inbound = vty[1] if vty[1] else "not set"
            v4_outbound = vty[2] if vty[1] else "not set"
            v6_inbound = vty[3] if vty[1] else "not set"
            v6_outbound = vty[4] if vty[1] else "not set"
            results[4].append(["vty %s" % vty[0], v4_inbound, v4_outbound])
            results[6].append(["vty %s" % vty[0], v6_inbound, v6_outbound])
        return results

    # main flow of the program starts here
    conn = Telnet(debug=0)
    conn.set_driver('ios')
    conn.connect(hostname)
    conn.login(account)
    conn.execute('terminal length 0')
    conn.auto_app_authorize(account)

    # map into structure:
    # policyname { (int, afi, direction) }
    map_pol_int = {}
    interfaces_overview = collect_interfaces(conn)
    for afi in interfaces_overview:
        for interface, inbound, outbound in interfaces_overview[afi]:
            # add inbound rules to map
            if inbound not in map_pol_int.keys():
                map_pol_int[inbound] = [{"int": interface,
                                        "afi": afi,
                                        "dir": "in"}]
            else:
                map_pol_int[inbound].append({"int": interface,
                                             "afi": afi,
                                             "dir": "in"})
            # add outbound
            if outbound not in map_pol_int.keys():
                map_pol_int[outbound] = [{"int": interface,
                                          "afi": afi,
                                          "dir": "in"}]
            else:
                map_pol_int[outbound].append({"int": interface,
                                             "afi": afi,
                                             "dir": "out"})
    print("INFO: interface / policy mapping:")
    pprint(map_pol_int)

    def lock_step(lock, pol):
        name = acls[pol]['name']
        afi = acls[pol]['afi']
        policy = acls[pol]['policy']
        print("INFO: uploading name: %s, afi: %s" % (name, afi))
        s(conn, 'configure terminal')
        if afi == 4:
            try:
                s(conn, "no ip access-list extended %s%s" % (lock, name))
            except:
                pass
            s(conn, "ip access-list extended %s%s" % (lock, name))
            for line in policy.split('\n'):
                s(conn, line)
        if afi == 6:
            try:
                s(conn, "no ipv6 access-list %s%s" % (lock, name))
            except:
                pass
            s(conn, "ipv6 access-list %s%s" % (lock, name))
            for line in policy.split('\n'):
                s(conn, line)
        s(conn, "end")

        # then replace ACL on all interfaces / VTYs
        if name in map_pol_int:
            for entry in map_pol_int[name]:
                if not entry['afi'] == afi:
                    continue
                print("INFO: lockstepping policy %s afi %s" % (name, afi))
                s(conn, "configure terminal")
                if entry['int'].startswith('vty '):
                    s(conn, "line %s" % entry['int'])
                    if afi == 4:
                        s(conn, "access-class %s%s %s"
                          % (lock, name, entry['dir']))
                    if afi == 6:
                        s(conn, "ipv6 access-class %s%s %s"
                          % (lock, name, entry['dir']))
                else:
                    s(conn, "interface %s" % entry['int'])
                    if afi == 4:
                        s(conn, "ip access-group %s%s %s"
                          % (lock, name, entry['dir']))
                    if afi == 6:
                        s(conn, "ipv6 traffic-filter %s%s %s"
                          % (lock, name, entry['dir']))
                s(conn, "end")

    for policy in acls:
        for lock in ["LOCKSTEP-", ""]:
            lock_step(lock, policy)
        # cleanup
        s(conn, "configure terminal")
        if acls[policy]['afi'] == 4:
            s(conn, "no ip access-list extended LOCKSTEP-%s"
              % acls[policy]['name'])
        if acls[policy]['afi'] == 6:
            s(conn, "no ipv6 access-list LOCKSTEP-%s"
              % acls[policy]['name'])
        s(conn, "end")
