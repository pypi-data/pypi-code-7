class Dummy:
    """
    This is a dummy adapter.
    It exists mostly for testing interfaces and does nothing, but returns
    success for every operation
    """
    def __init__(self, namespace, ttl, config):
        self.ttl = ttl
        self.namespace = namespace
        self.config = config




