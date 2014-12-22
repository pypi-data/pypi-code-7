
# python standard library
import socket
import os
import errno
import time

# third-party
import paramiko


client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#client.load_system_host_keys()

try:
    client.connect('badhostname', username='fakeuser')
except IOError as error:
    print error


print "ENOENT: {0} '{1}'".format(errno.ENOENT, os.strerror(errno.ENOENT))


try:
    client.connect('localhost', username='ummagumma')
except paramiko.PasswordRequiredException as error:
    print error


try:
    client.connect('localhost', username='fakeuser', password='badpassword')
except paramiko.AuthenticationException as error:
    print error


client.connect('localhost', username='fakeuser', password=None)
i,o,e = client.exec_command('ps -e | grep iperf')
for line in o:
    pid = line.split()[0]
    client.exec_command('kill -9 {0}'.format(pid))
time.sleep(0.1)

stdin, stdout, stderr = client.exec_command('iperf -s', timeout=0.1)

try:
    for line in stdout:
        print line
    for line in stderr:
        print line
except socket.timeout as error:
    print "socket.timeout doesn't give an error message"
    print error


stdin, stdout, stderr = client.exec_command('iperf -v')
for line in stderr:
    print line
