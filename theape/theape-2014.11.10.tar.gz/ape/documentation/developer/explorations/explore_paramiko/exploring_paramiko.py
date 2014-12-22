
# third-party
import paramiko
from paramiko import SSHClient

# this package
from ape.commoncode.code_graphs import module_diagram, class_diagram


# paramiko is using __init__.py to elevate the SSHClient to the top level
# you need to add the module name yourself or the module diagram will try __init__.py
# and be empty
client_file =  paramiko.__file__.replace("__init__.py", "client.py")


name = module_diagram(module=client_file,
                      project='paramiko')
print ".. image:: {0}".format(name)
print "   :align: center"


name = class_diagram(class_name='SSHClient', module=client_file)
print ".. figure:: {0}".format(name)
print "   :align: center"


client = SSHClient()
try:
    client.connect('localhost', username='fakeuser')
except paramiko.SSHException as error:
    print error    


client.load_system_host_keys()
try:
    client.connect('localhost', username='fakeuser')
except paramiko.SSHException as error:
    print error


# this was in the ape
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.load_system_host_keys()

try:
    client.connect('localhost', username='fakeuser')
    stdin, stdout, stderr = client.exec_command('ls')
    for line in stdout:
        print "StdOut: {0}".format(line)

except (IOError, paramiko.SSHException) as error:
    print error
