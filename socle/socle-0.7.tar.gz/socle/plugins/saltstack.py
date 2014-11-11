
import os
from socle.menu import choice, CanceledException
import logging

logger = logging.getLogger(__name__)

def reset_minion_keys():
    try:
        os.unlink("/etc/salt/pki/minion/minion.pub")
    except OSError:
        pass
        
    try:
        os.unlink("/etc/salt/pki/minion/minion.pem")
    except OSError:
        pass
    
def reset_master_pub():
    try:
        os.unlink("/etc/salt/pki/minion/minion_master.pub")
    except OSError:
        pass

def reconfigure_salt_minion():
   
    if minion_pub:
        description = "Minion fingerprint: %s\n" % minion_pub
    else:
        description = "Minion key not generated\n"
        
    if master_pub:
        description += "Master fingerprint: %s\n" % master_pub
    else:
        description += "Not associated with master\n"


    choices = (
        ("Reconfigure Salt master hostname", NotImplemented),
        ("Reset Salt minion key", reset_minion_keys),
        ("Clear Salt master certificate", reset_master_pub)
    )


    while True:
        try:
            action = choice(
                choices,
                "Reconfigure SaltStack",
                description)
        except CanceledException:
            return
        action()
    
    
try:
    from salt.utils import pem_finger
    
    minion_pub = pem_finger("/etc/salt/pki/minion/minion.pub")
    master_pub = pem_finger("/etc/salt/pki/minion/minion_master.pub")
    
    MENU_ENTRIES = (
        ("SaltStack", reconfigure_salt_minion),
    )
    logger.info("Salt configuration enabled")
except ImportError:
    MENU_ENTRIES = ()
    logger.info("Salt configuration disabled")
