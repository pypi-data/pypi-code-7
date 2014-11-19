import time
import socket
import paramiko
import logging
import collections

LOG = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
LOG.addHandler(ch)
LOG.setLevel(logging.DEBUG)


class RemoteClient(object):

    def __init__(self, host, username, password=''):
        self.host = host
        self.username = username
        self.password = password

    def ping_host(self, host, num_pings=1):
        cmd = "ping -c %d -w %d %s  | tail -1 | awk '{print $4}' | cut -d '/' -f2" % (num_pings, num_pings, host)
        result = self._exec_command(cmd)
        if result.exit_code == 0:
            return result.stdout.readlines()[0].rstrip()
        else:
            return 0

    def _exec_command(self, cmd):
        ssh = self._get_ssh_connection()
        stdin,stdout,stderr=ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        result = collections.namedtuple('res', 'stdin stdout stderr exit_code')
        return result(stdin,stdout,stderr,exit_status)

    def _get_ssh_connection(self, sleep=1.5, backoff=1):
        bsleep = sleep
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        LOG.info("Creating ssh connection to '%s' as '%s'"
                 " with password %s",
                 self.host, self.username, str(self.password))
        attempts = 0
        while True:
            try:
                ssh.connect(self.host, username=self.username,
                            password=self.password)
                LOG.info("ssh connection to %s@%s successfuly created",
                         self.username, self.host)
                return ssh
            except (socket.error,
                    paramiko.SSHException) as e:
                bsleep += backoff
                attempts += 1
                LOG.warning("Failed to establish authenticated ssh"
                            " connection to %s@%s (%s). Number attempts: %s."
                            " Retry after %d seconds.",
                            self.username, self.host, e, attempts, bsleep)
                time.sleep(bsleep)
