
import os
import pytz
from socle.menu import choice
from socle.atomic import AtomicWrite

def reconfigure_timezone():
    """
    Yeah we could have simply issued dpkg-reconfigure tzdata, but where's the fun in that?
    Well this one should be pretty platform agnostic and should work over the UART aswell.
    """
    
    superset = sorted(set([j.split("/", 1)[0] for j in pytz.all_timezones if "/" in j]))
            
    superselection = choice([(j,j) for j in superset],
        "Reconfigure timezone",
        "Please select geographic area in which this machine is located:")
        
    superselection += "/"

    subset = sorted([j[len(superselection):] for j in pytz.all_timezones if j.startswith(superselection)])

    subselection = choice([(j,j) for j in subset],
        "Reconfigure timezone",
        "Please select the city or region corresponding to your timezone:")
        
    with AtomicWrite("/etc/timezone") as fh:
        fh.write(superselection + subselection + "\n")

    # Update /etc/localtime symlink
    if os.path.exists("/etc/localtime.part"):
        os.unlink("/etc/localtime.part")
    os.symlink("/usr/share/zoneinfo/" + superselection + subselection, "/etc/localtime.part")
    os.rename("/etc/localtime.part", "/etc/localtime")

if os.path.exists("/usr/share/zoneinfo"):
    MENU_ENTRIES = (
        ("Set timezone", reconfigure_timezone),
    )
else:
    MENU_ENTRIES = ()
    print "It seems /usr/share/zoneinfo does not exist, are you sure tzdata package is installed? Disabling timezone selection for now"
