#!/usr/bin/python
"""
Usage: xtrabackup_send.py <hostname>
Author: Matthieu 'Korrigan' Rosinski <mro@quanta-computing.com>

This script runs xtrabackup and pipe the output to <hostname>


"""
import subprocess
import argparse


opts = None


def main():
    """
    Main entry point for xtrabackup_send

    """
    global opts

    parser = argparse.ArgumentParser(
        description='This program is a wrapper for sending xtrabackup to a target over SSH',
        epilog='Copyright Quanta-computing 2014',
        )
    parser.add_argument('-u', '--user', help='Specifies the remote user to use for SSH auth')
    parser.add_argument('-k', '--ssh-key', help='Specified a custom ssh key to use')
    parser.add_argument('-d', '--debug', action='store_true', help='Switch to loglevel DEBUG')
    parser.add_argument('host', help='The remote hostname or IP address')
    opts = parser.parse_args()
    send_backup(opts.host)


def send_backup(host):
    """
    Executes innobackupex and pipe it trough gzip and ssh

    """
    ssh_host = host
    ssh_key = []
    if opts.user:
        ssh_host = "{}@{}".format(opts.user, ssh_host)
    if opts.ssh_key:
        ssh_key = ['-i', opts.ssh_key]
    ssh = subprocess.Popen(['ssh', ssh_host] + ssh_key,
                           stdin=subprocess.PIPE)
    gzip = subprocess.Popen(['gzip', '-q', '-c', '-'],
                            stdin=subprocess.PIPE,
                            stdout=ssh.stdin)
    xtrabackup = subprocess.Popen(['innobackupex', '--stream=tar', '/tmp'],
                                  stdout=gzip.stdin)
    xtrabackup.communicate()
    gzip.wait()
    ssh.wait()


if __name__ == "__main__":
    main()
