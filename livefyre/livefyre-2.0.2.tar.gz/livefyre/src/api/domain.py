from livefyre.src.utils import get_network_from_core


class Domain(object):
    @staticmethod
    def quill(core):
        network = get_network_from_core(core)
        return 'https://{0}.quill.fyre.co'.format(network.network_name) if network.ssl else 'http://quill.{0}.fyre.co'.format(network.network_name)
    
    @staticmethod
    def bootstrap(core):
        network = get_network_from_core(core)
        return 'https://{0}.bootstrap.fyre.co'.format(network.network_name) if network.ssl else 'http://bootstrap.{0}.fyre.co'.format(network.network_name)
