# multilogger_collectd - AREXX Multilogger collectd plugin
# Copyright (c) 2014 Pirmin Kalberer
#
# This file is part of arexx-multilogger-collectd-plugin.
# arexx-multilogger-collectd-plugin is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <http://www.gnu.org/licenses/>.


""" multilogger_collectd - AREXX Multilogger collectd plugin """

import collectd  # pylint: disable=import-error
from multilogger import Multilogger
from datetime import datetime


class MultiloggerCollectd(Multilogger):
    """ Collect data from AREXX Multilogger and dispatch them to collectd """

    PLUGIN_NAME = 'multilogger'

    def __init__(self):
        Multilogger.__init__(self, action=self._read_data)
        self._sensor_value = {}  # sensor-id -> value: [timestamp, value]
        self._sensor_config = {}  # sensor-id -> {"name": str, "offset": float}

    def callback_configure(self, config):
        """ Configure callback """
        collectd.info("multilogger_collectd: callback_configure")
        for node in config.children:
            if node.key == "Sensor":
                sensor_config = self._sensor_config[node.values[0]] = {}
                for subnode in node.children:
                    if subnode.key == "Name":
                        sensor_config["name"] = subnode.values[0]
                    elif subnode.key == "Offset":
                        sensor_config["offset"] = subnode.values[0]
                    else:
                        collectd.warning(
                            'multilogger_collectd: Unknown config %s'
                            % subnode.key)
            else:
                collectd.warning(
                    'multilogger_collectd: Unknown config %s' % node.key)

    def callback_init(self):
        """ Init callback

            Initialize the connection to the AREXX Multilogger
        """
        collectd.info("multilogger_collectd: callback_init")
        try:
            self.connect()
        except Exception as e:
            collectd.error("multilogger_collectd: %s" % str(e))

    def callback_read(self):
        """ Read callback

            Read data from the AREXX Multilogger and dispatch values
            to collectd.
        """
        collectd.info("multilogger_collectd: callback_read")
        self.read_data_buffer()
        try:
            self.read_data_buffer()
            # calls read_data, which writes values into self._sensor_value
        except Exception as e:
            collectd.error("multilogger_collectd: %s" % str(e))

        # Delete old data
        for sensor, (timestamp, value) in self._sensor_value.items():
            if (datetime.now() - timestamp).total_seconds() > 120:
                del self._sensor_value[sensor]
                collectd.info("multilogger_collectd: sensor value with"
                              " timestamp=%s dropped" % timestamp)

        for sensor, (timestamp, value) in self._sensor_value.iteritems():
            collectd.info("multilogger_collectd: sensor=%s timestamp=%s"
                          " value=%s" % (sensor, timestamp, value))
            config = self._sensor_config.get(sensor, {})
            name = config.get("name", sensor)
            offset = config.get("offset", 0)
            self._dispatch_value(name, value+offset)

    def _read_data(self, data):
        #data = [clock, sensor, valueRaw, value]
        row = "\t".join([str(i) for i in data])
        collectd.info(row)
        self._sensor_value[str(data[1])] = [data[0], data[3]]

    def _dispatch_value(self, name, value):
        """ Dispatch value to collectd """
        val = collectd.Values()
        val.plugin = self.PLUGIN_NAME
        #val.plugin_instance = ''
        val.type = 'gauge'
        val.type_instance = name
        val.values = [value]
        val.dispatch()


MC = MultiloggerCollectd()
collectd.register_config(MC.callback_configure)
collectd.register_init(MC.callback_init)
collectd.register_read(MC.callback_read)
