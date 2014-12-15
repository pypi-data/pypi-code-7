import json
from datetime import datetime
from datetime import timedelta
from collections import namedtuple
import collections
from urlparse import urljoin
import os.path
import sys
import re

import requests


# need to figure out error handling.

BASE_URL = 'https://api.serverdensity.io'
CONFIG_PATH = '~/.config.json'

Bandwidth = namedtuple('Bandwidth', 'rxgb, txgb')


# ###### API section #########


def parse_response(response):
    try:
        data = json.loads(response.text)
    except ValueError:
        data = {}
    try:
        if response.status_code == 200:
            return data
        elif not data:
            data['message'] = 'There was no response'
            raise Exception
        elif response.status != 200:
            raise Exception
    except Exception:
        sys.exit('Error: {0}'.format(data['message']))
        # exit to os.


def get_jsondata(urlpath, payload):
    response = requests.get(urljoin(BASE_URL, urlpath), params=payload)
    return parse_response(response)


def available_metrics(config):
    payload = {
                'token': config['api_key'],
                'start': config['start'],
                'end': config['end']
                }

    api_response = get_jsondata('metrics/definitions/{0}'.format(config['current_device']), payload)

    return api_response


def bandwidth_response(config):
    # Note: from groups I would like to set device id and interface.
    """Get total_bandwidth for current device and current interface"""

    filters = {
        'networkTraffic': ['rxMByteS', 'txMByteS']
    }

    payload = {
                'token': config['api_key'],
                'start': config['start'],
                'end': config['end'],
                'filter': json.dumps(filters)
                }

    api_response = get_jsondata('metrics/graphs/{0}'.format(config['current_device']), payload)

    return api_response


def available_devices():
    config = read_config()
    payload = {'token': config['api_key']}

    api_response = get_jsondata('/inventory/devices', payload)
    return api_response

# ###### API section ends ######

# ##### Working with responses #######


def get_network_interfaces(metrics):
    """Gives you a list of network adapters from available_metrics"""
    network = {}
    adapters = []
    for j in metrics:
        if j.get('key') == 'networkTraffic':
            network = j
            break

    for adapter in network['tree']:
        adapters.append(adapter['key'])

    return adapters


def get_interfaces(bandwidth_response):
    interfaces = bandwidth_response[0]['tree']
    interfaces_list = [interface['name'] for interface in interfaces]
    return interfaces_list


def get_devices(device_response):
    devicedic = {}
    for device in device_response:
        devicedic[device['name']] = {'_id': device['_id']}
    return devicedic


def calc_bandwidth_interface(device_bandwidth):
    """Takes input from device_bandwidth, for all network interfaces."""
    # NOTE: need to adjust this for several eth.
    # second list is the interface. for
    rxmbslist = device_bandwidth[0]['data']
    txmbslist = device_bandwidth[1]['data']
    if rxmbslist[1]['x'] - rxmbslist[0]['x'] < 3600:
        # Every datapoint represents one minute.
        rxgb = sum([value['y']*60 for value in rxmbslist])/1000
        txgb = sum([value['y']*60 for value in txmbslist])/1000
    else:
        rxgb = sum([value['y']*3600 for value in rxmbslist])/1000
        txgb = sum([value['y']*3600 for value in txmbslist])/1000

    # There two definitions though
    # http://en.wikipedia.org/wiki/Gigabyte#Definition



    return Bandwidth(rxgb, txgb)


def read_config():
    config = {}
    try:
        with open(os.path.expanduser(CONFIG_PATH), 'r') as f:
            config = json.load(f)
    except IOError:
        print "\nError: There is no config.json file"
    return config


def modify_config(keydic):
    config = read_config()
    for key, val in keydic.iteritems():
        config[key] = val
    with open(os.path.expanduser(CONFIG_PATH), 'w') as fp:
        json.dump(config, fp)
    return config


def sum_bandwidth(group_calc):
    """Helper to calc_bandwidth_group"""
    for interface, dic in group_calc.iteritems():
        txgb = 0
        rxgb = 0
        for name, bw in dic.iteritems():
            txgb += bw.txgb
            rxgb += bw.rxgb
        group_calc[interface]['total'] = Bandwidth(rxgb, txgb)
    return group_calc


def calc_bandwidth_group(groupname):
    config = read_config()
    group_calc = {}
    if not config['groups']:
        raise KeyError
    group = config['groups'][groupname]
    for devicename, devicedic in group.iteritems():
        print "Fething data for {}...".format(devicename)
        try:
            device = calc_bandwidth_device(devicename)
            for interface, bw in device.iteritems():
                group_calc.setdefault(interface, {}).update({devicename:bw})
        except KeyError:
            print "{} has no data for this period, therefore excluding it.".format(
                devicename)
    calc_total = sum_bandwidth(group_calc)
    return calc_total


def calc_bandwidth_device(devicename):
    config = read_config()
    config['current_device'] = config['devices'][devicename]['_id']

    bandwidth_resp = bandwidth_response(config)
    device_bandwidth = {}
    for interface in bandwidth_resp[0]['tree']:
        device_bandwidth[interface['name']] = calc_bandwidth_interface(
                                interface['tree'])
    return device_bandwidth


# ######## CLI API ########

def update_groups():
    device_response = available_devices()
    config = read_config()
    if not config['devices']:
        print "No devices found in config file, updating devices..."
        update_devices()
        config = read_config()

    groupdic = {}
    for device in device_response:
        groupdic.setdefault(device['group'], {})
        groupdic[device['group']].update({
            device['name']: {
                '_id': device['_id']
            }
        })

    print "Updated groups and saved it to config files."
    config['groups'] = groupdic
    modify_config(config)


def print_groups():
    config = read_config()
    if not config['groups']:
        print "There are no groups, try 'groups update' first"
    for groupname, groupdic in config['groups'].iteritems():
        print "Group: {}".format(groupname)
        for device, devicedic in groupdic.iteritems():
            print "    {}".format(device)
        print "\n"


def print_devices():
    config = read_config()
    try:
        devicedic = config['devices']

        for name, dic in devicedic.iteritems():
            print "Device: {0}\nID: {1}\n".format(
                name, dic['_id'])

        # for name, dic in devicedic.iteritems():
        #     print "Device: {0}\nID: {1}\nInterfaces: {2}\n".format(
        #         name, dic['_id'], ", ".join(dic['interface']))
    except KeyError as e:
        sys.exit('Error: There are no devices')


def update_devices():
    response = available_devices()
    devices = get_devices(response)
    config = read_config()
    # for name, dic in devices.iteritems():
    #     config['current_device'] = dic['_id']
    #     response = bandwidth_response(config)
    #     interfaces = get_interfaces(response)
    #     devices[name].update({'interface': interfaces})
    config['devices'] = devices
    modify_config(config)
    print "Updated devices and saved it to config files."

# print_bandwidth_group('Web')

def print_bandwidth_group(groupname, start=None, end=None):
    if start:
        modify_config({'start': start, 'end': end})

    config = read_config()
    try:
        group = config['groups'][groupname]

        group = calc_bandwidth_group(groupname)

        print "\n{0:25}{1:7}{2:>10}{3:>10}".format(
            'Device', 'Interface', 'RxGB', 'TxGB')
        for interface, devicedic in group.iteritems():
            for devicename, bw in devicedic.iteritems():
                if devicename != 'total':
                    print "{0:25}{1:7}{2:{rtxwidth}{prec}}{3:{rtxwidth}{prec}}".format(
                        devicename, interface, bw.rxgb, bw.txgb,
                        rtxwidth=">12",
                        prec=".2f"
                    )
            total = group[interface]['total']
            if total.rxgb > 1000:
                print "Total received: {:.2f} tb".format(total.rxgb/1000)
            else:
                print "Total recieved: {:.2f} gb".format(total.rxgb)
            if total.txgb > 1000:
                print "Total sent: {:{width}{prec}} tb".format(
                    total.txgb/1000, width=">5", prec=".2f")
            else:
                print "Total sent: {:{width}{prec}} gb".format(
                    total.txgb, width=">5", prec=".2f")
            print "\n"
    except KeyError:
        print "Error: Couldn't find the group '{0}'".format(groupname)


def print_bandwidth_device(devicename, start=None, end=None):
    config = read_config()
    # Note: Make time amends.
    try:
        calc = calc_bandwidth_device(devicename)
        print devicename
        print "{0:5}{1:5}{2:>10}{3:>10}".format(
            '', 'Interface', 'RxGB', 'TxGB')
        for interface, bw in calc.iteritems():
            print "{0:5}{1:5}{2:>14}{3:>10}".format(
                '', interface, round(bw.rxgb, 2), round(bw.txgb, 2))
    except KeyError:
        sys.exit("Error: {0} doesn't have any data for this period".format(devicename))


def check_existing_apikey():
    config = read_config()
    if not config['api_key']:
        print "You need an authentication token"
        apikey = raw_input("What is your token: ")
        auth_apikey(apikey)


def update_current_time():
    # Date format: YYYY-MM-DDTHH:MM:SSZ
    end_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    start_time = (
        datetime.now() - timedelta(hours=1)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
    config = read_config()
    set_time(start_time, end_time)


def auth_apikey(apikey):
    payload = {
        "token": apikey,
        "fields": json.dumps(['name'])
        }
    data = get_jsondata('inventory/devices', payload)
    if data:
        print "Token verified."
        modify_config({'api_key': apikey})


def set_time(start, end):
    config = read_config()
    m = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
    if not m.match(start) and not m.match(end):
        sys.exit("This is not the right time format")
    config.update({'start': start, 'end': end})
    modify_config(config)
    print_time()


def print_time():
    config = read_config()
    print "\nYou are now using the current timeperiod."
    print "Start time: {}\nEnd time: {}".format(
        config['start'], config['end'])


if __name__ == '__main__':
    config = read_config()
    # devices = available_devices()
    # metrics = available_metrics()
    # bandwidth = bandwidth_response(config)

    # device_names = get_devices(devices)
    # adapters = get_network_interfaces(metrics)
    # total_bandwidth = calculate_bandwidth(bandwidth)
