from fabfile import*
from fabric.context_managers import settings
from fabric.api import execute

execute (copyfileremote, 'x', 'Ipan')
