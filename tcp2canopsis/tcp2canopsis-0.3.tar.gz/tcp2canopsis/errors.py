# -*- coding: utf-8 -*-


class ConnectorError(Exception):
    def __init__(self, msg):
        super(ConnectorError, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return '{0}: {1}'.format(self.__class__.__name__, self.msg)
