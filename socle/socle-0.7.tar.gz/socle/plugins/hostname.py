
from socle.menu import form
from socle.atomic import AtomicWrite

def reconfigure_hostname():
    current_hostname = open("/etc/hostname").readline().strip()
    FIELDS = (
        ("Hostname", current_hostname),
    )
    
    new_hostname, = form(
        FIELDS,
        "Set hostname",
        "Enter hostname:")
        
    with AtomicWrite("/etc/hostname") as fh:
        fh.write(new_hostname)

    # TODO: Substitute lines in /etc/hosts
    
MENU_ENTRIES = (
    ("Set hostname", reconfigure_hostname),
)

