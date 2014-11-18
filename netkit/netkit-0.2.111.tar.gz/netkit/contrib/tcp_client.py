# -*- coding: utf-8 -*-

import socket
from netkit.stream import Stream


class TcpClient(object):
    """
    封装过的tcp client
    """

    box_class = None
    host = None
    port = None
    timeout = None
    stream = None

    def __init__(self, box_class, host, port, timeout=None):
        self.box_class = box_class
        self.host = host
        self.port = port
        self.timeout = timeout

    def connect(self):
        """
        连接服务器，失败会抛出异常
        :return:
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((self.host, self.port))
        except Exception, e:
            sock.close()
            raise e

        self.stream = Stream(sock)

    def read(self):
        """
        如果超时会抛出异常 socket.timeout
        :return:
        """
        if self.closed():
            return None

        data = self.stream.read_with_checker(self.box_class.instance().check)
        if not data:
            return None

        box = self.box_class()
        box.unpack(data)

        return box

    def write(self, data):
        """
        写入
        :param data:
        :return:    True/False
        """
        if self.closed():
            return False

        if isinstance(data, self.box_class):
            data = data.pack()

        return self.stream.write(data)

    def close(self):
        if not self.stream:
            return

        return self.stream.close()

    def closed(self):
        if not self.stream:
            return True

        return self.stream.closed()
