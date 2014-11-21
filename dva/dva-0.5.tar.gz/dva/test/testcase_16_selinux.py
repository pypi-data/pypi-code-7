""" This module contains testcase_16_selinux test """
from testcase import Testcase


class testcase_16_selinux(Testcase):
    """
    SELinux should be in enforcing/targeted mode
    """

    stages = ['stage1']
    tags = ['default']

    # pylint: disable=W0613
    def test(self, connection, params):
        """ Perform test """

        self.ping_pong(connection, 'getenforce', '\r\nEnforcing\r\n')
        self.get_return_value(connection, 'grep \'^SELINUX=enforcing\' /etc/sysconfig/selinux')
        self.get_return_value(connection, 'grep \'^SELINUXTYPE=targeted\' /etc/sysconfig/selinux')
        self.ping_pong(connection, 'setenforce Permissive && getenforce', '\r\nPermissive\r\n')
        self.ping_pong(connection, 'setenforce Enforcing && getenforce', '\r\nEnforcing\r\n')
        return self.log
