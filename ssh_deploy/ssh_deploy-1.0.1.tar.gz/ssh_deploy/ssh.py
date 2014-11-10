#!/usr/local/python
import paramiko
import argparse
import subprocess
import status

__all__ = ['deploy', 'gen_ssh_keygen']

def deploy(server, username, passwd, remote_script="/tmp/remote_script.sh"):
    local_script = _gen_remote_script()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh_client.connect(server, username=username, password=passwd)
        sftp_client = paramiko.SFTPClient.from_transport(ssh_client.get_transport())
    except socket.error:
        return status.CONNECTION_FAILURE
    except paramiko.AuthenticationException:
        return status.AUTH_FAILURE
    except paramiko.SSHException:
        return status.SSH_FAILURE
    try:
        sftp_client.put(local_script, remote_script)
    except IOError:
        return status.IO_FAILURE

    stdin, stdout, stderr = ssh_client.exec_command('/bin/bash %s' % remote_script)
    if not stdout.channel.recv_exit_status() == 0:
        print (not stdout.channel.recv_exit_status())
        print ("out: %s\n err: %s\n" %(stdout.read().strip(), stderr.read().strip()))
        return status.UNKNOWN_ERROR
    sftp_client.remove(remote_script)
    return stdout.read().strip()

def gen_ssh_keygen():
    subprocess.call("expect ./gen_keygen.sh", shell=True)

def _gen_remote_script():
    remote_script = subprocess.check_output("bash ./gen_remote_script.sh", shell=True)
    return remote_script.strip()

def _parse_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, help='remote host', required=True)
    parser.add_argument('--user', type=str, help='login user', required=True)
    parser.add_argument('--passwd', type=str, help='login password', required=True)
    args = parser.parse_args()
    return args.host, args.user, args.passwd

if __name__ == "__main__":
    server, username, passwd = _parse_argument()
    ret = deploy(server, username, passwd)
    print ret
