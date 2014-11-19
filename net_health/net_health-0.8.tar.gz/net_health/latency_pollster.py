#
# Copyright 2012 eNovance <licensing@enovance.com>
# Copyright 2012 Red Hat, Inc
#
# Author: Julien Danjou <julien@danjou.info>
# Author: Eoghan Glynn <eglynn@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import ceilometer
from ceilometer.compute import plugin
from ceilometer.compute.pollsters import util
from ceilometer.compute.virt import inspector as virt_inspector
from ceilometer.openstack.common.gettextutils import _
from ceilometer.openstack.common import log
from ceilometer import sample

LOG = log.getLogger(__name__)


class LatencyPollster(plugin.ComputePollster):

    def get_samples(self, manager, cache, resources):
        for instance in resources:
            LOG.debug(_('checking instance %s'), instance.id)
            instance_name = util.instance_name(instance)
            try:
                cpu_info = manager.inspector.inspect_cpus(instance_name)
                LOG.debug(_("CPUTIME USAGE: %(instance)s %(time)d"),
                          {'instance': instance.__dict__,
                           'time': cpu_info.time})
                cpu_num = {'cpu_number': cpu_info.number}
                yield util.make_sample_from_instance(
                    instance,
                    name='latency',
                    type=sample.TYPE_GAUGE,
                    unit='ms',
                    volume="",
                    additional_metadata="",
                )
            except virt_inspector.InstanceNotFoundException as err:
                # Instance was deleted while getting samples. Ignore it.
                LOG.debug(_('Exception while getting samples %s'), err)
            except Exception as err:
                LOG.exception(_('could not get latency for %(id)s: %(e)s'),
                              {'id': instance.id, 'e': err})
