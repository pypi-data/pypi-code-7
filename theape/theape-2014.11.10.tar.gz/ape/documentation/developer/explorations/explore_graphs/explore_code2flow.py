
# python standard library
import subprocess
import shlex

# this package
import ape.plugins.apeplugin as plugin


file_name = plugin.__file__.rstrip('c')
command = 'code2flow --language py -o plugin_flow.png {0}'.format(file_name)
subprocess.call(shlex.split(command))
