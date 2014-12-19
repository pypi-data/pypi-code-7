# -*- coding: UTF-8 -*-
from os import environ, path, unlink
from zabbix_client import ZabbixServerProxy
from UserDict import UserDict
import json

CRITICAL = 'critical'
WARNINGS = 'warnings'

CRITICAL_SYMBOLE = u'🔥'
WARNINGS_SYMBOLE = u'⚠️'

SYMBOLE_NODIFF = u'±'
SYMBOLE_ADD = u' ↑'
SYMBOLE_NEGATIVE = u' ↓'


class JsonDataStore(UserDict, object):

    def __init__(self, initialdata={}):
        file_name = self.get_filename()
        if path.exists(file_name):
            with open(file_name) as json_file:
                try:
                    self.data = json.load(json_file)
                except:
                    self.data = {}
        else:
            self.data = initialdata

    def __del__(self):
        file_name = self.get_filename()
        if self.data:
            with open(file_name, 'w') as json_file:
                self.data = json.dump(self.data, json_file)
        else:
            if path.exists(file_name):
                unlink(file_name)

    def get_filename(self):
        tmp_dir = environ.get('TMPDIR')
        file_name = 'storage.json'
        return path.join(tmp_dir, file_name)


class ZabbixAgent(object):

    def __init__(self, username, password, endpoint):
        self.conn = ZabbixServerProxy(endpoint)
        self.conn.user.login(user=username, password=password)

    def get_current_high_triggers(self):

        return self.conn.trigger.get(
            filter={'priority': [4, 5]},
            only_true='true', monitored=1, withUnacknowledgedEvents='true')

    def get_current_warning_triggers(self):

        return self.conn.trigger.get(
            filter={'priority': [1, 2, 3]},
            only_true='true', monitored=1, withUnacknowledgedEvents='true')


def zabbix_current_active(pl, username, password, endpoint):

    zabbix = ZabbixAgent(username, password, endpoint)
    triggers_high = zabbix.get_current_high_triggers()
    triggers_low = zabbix.get_current_warning_triggers()

    if triggers_high:
        level = 100
    elif triggers_low:
        level = triggers_low
    else:
        level = 0

    return [{
        'contents': u"H[%s] W[%s]" % (len(triggers_high), len(triggers_low)),
        'highlight_group': [
            'zabbix_current_state_gradient', 'zabbix_current_state'],
        'divider_highlight_group': 'background:divider',
        'gradient_level': level
    }]


def active_triggers(pl, username, password, endpoint, triggers='warnings'):
    zabbix = ZabbixAgent(username, password, endpoint)
    storage = JsonDataStore()

    count_trigger_key = 'current_count_%s' % (triggers)
    count_delta_key = 'last_delta_%s' % (triggers)

    if triggers == WARNINGS:
        active_triggers = zabbix.get_current_warning_triggers()
        symbole = WARNINGS_SYMBOLE
        highlight_group = 'active_triggers_%s' % (WARNINGS)

    elif triggers == CRITICAL:
        active_triggers = zabbix.get_current_high_triggers()
        symbole = CRITICAL_SYMBOLE
        highlight_group = 'active_triggers_%s' % (CRITICAL)

    triggers_count = len(active_triggers)

    if count_trigger_key in storage:
        if storage[count_trigger_key] != triggers_count:
            delta = triggers_count - storage[count_trigger_key]
            if delta == triggers_count:
                delta = 0
            sign = SYMBOLE_NEGATIVE if delta < 0 else SYMBOLE_ADD

            storage[count_delta_key] = delta
            storage[count_trigger_key] = triggers_count
        else:
            storage[count_trigger_key] = triggers_count
            if count_delta_key in storage:
                delta = storage[count_delta_key]
                sign = SYMBOLE_NEGATIVE if delta < 0 else SYMBOLE_ADD
            else:
                delta = 0
                sign = SYMBOLE_NODIFF

    else:
        storage[count_trigger_key] = triggers_count
        sign = SYMBOLE_NODIFF
        delta = 0
        storage[count_delta_key] = delta

    return [{
        'contents': u"%s %s%s%s" % (
            symbole, triggers_count, sign, abs(delta)),
        'highlight_group': [highlight_group]
    }]
