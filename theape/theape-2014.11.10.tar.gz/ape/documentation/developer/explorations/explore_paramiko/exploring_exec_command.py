
from paramiko import SSHClient
import paramiko


client = SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('localhost', username='fakeuser')
stdin, stdout, stderr = client.exec_command("nmap -sP '192.168.103.*'")
for line in stdout:
    print line


stdin, stdout, stderr = client.exec_command('sudo nmap -sP "192.168.103.*"', get_pty=True)
stdin.write('fakepassword\n')
for line in stdout:
    print line    
