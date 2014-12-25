"""
Carbon settings options:

CARBON_HOST            - target address where statistics will be send
CARBON_PORT            - carbon server port, defaylt is 2003
CARBON_AGGREGATOR_PORT - port of the carbon aggregator,
                         None mean no aggregator
CARBON_HOSTNAME        - source host name, None trigger hostname resolve
CARBON_PREFIX          - global metrica prefix
CARBON_SEND_ALL        - send additional metric where hostname
                         replaced with 'all'
CARBON_SEND_COUNT      - send extra metic with .count suffix and 1 value

"""

class ConfiManager(object):
    """
    Proxy config manager
    """
    DEFAULT = {
        'CARBON_HOST': 'localhost',
        'CARBON_PORT': 2003,
        'CARBON_AGGREGATOR_PORT': None,
        'CARBON_HOSTNAME': None,
        'CARBON_PREFIX': None,
        'CARBON_SEND_ALL': False,
        'CARBON_SEND_COUNT': False,
    }

    def __init__(self):
        self.parent = object()

    def __getattr__(self, key):
        if hasattr(self.parent, key):
            return getattr(self.parent, key)
        return self.DEFAULT.get(key)

    def set_parent(self, parent):
        self.parent = parent


settings = ConfiManager()
