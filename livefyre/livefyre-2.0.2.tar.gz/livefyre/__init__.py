from .src.core.network import Network


class Livefyre(object):
    @staticmethod
    def get_network(network_name, network_key):
        return Network.init(network_name, network_key)