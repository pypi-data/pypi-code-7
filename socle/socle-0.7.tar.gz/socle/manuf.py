
import re
import os

RE_OUI = "([\da-f]{2}:){2}[\da-f]{2}$"
MANUFACTURERS = None


# To install manufacturer database: apt-get install libwireshark-data

def load():
    global MANUFACTURERS

    try:
        fh = open("/usr/share/wireshark/manuf")
    except IOError:
        MANUFACTURERS = dict()
        return
    while True:
        line = fh.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue

        oui, remainder = line.split("\t", 1)
        oui = oui.lower()
        if not re.match(RE_OUI, oui):
            continue
        if "#" in remainder:
            _, remainder = remainder.split("#", 1)
            remainder = remainder.strip()
        MANUFACTURERS[oui] = remainder

def get(hardware_address, fallback="Unknown"):
    global MANUFACTURERS
    if MANUFACTURERS == None:
        MANUFACTURERS = {}
        try:
            load()
        except OSError:
            pass
    return MANUFACTURERS.get(hardware_address[:8], fallback)
