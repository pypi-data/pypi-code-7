from ceilometer.compute import plugin
from ceilometer.compute.pollsters import util
from ceilometer.openstack.common import log
from ceilometer.openstack.common.gettextutils import _
from ceilometer import sample
import subprocess

LOG = log.getLogger(__name__)


class LatencyPollster(plugin.ComputePollster):

    @staticmethod
    def get_samples(manager, cache, instance):
        LOG.debug(_('checking instance %s'), instance.id)
        instance_name = util.instance_name(instance)
        LOG.debug(_(' instance %s'), instance_name)
        try:
            proc = subprocess.Popen(["/usr/local/bin/check_connectivity %s" % instance], stdout=subprocess.PIPE, shell=True)
            out, err = proc.communicate()
            yield util.make_sample_from_instance(
                    instance,
                    name='latency',
                    type=sample.TYPE_GAUGE,
                    unit='ms',
                    volume=out,
            )
        except Exception as err:
            LOG.exception(_('could not get latency for %(id)s: %(e)s'),
                    {'id': instance.id, 'e': err})
