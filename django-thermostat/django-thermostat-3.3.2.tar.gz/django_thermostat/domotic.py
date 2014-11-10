from hautomation_restclient import cmds
from settings import *
import requests
from time import *


def start_flame():
    try:
        cmds.pl_switch(
            HEATER_PROTOCOL,
            HEATER_DID,
            "on",
            HEATER_API,
            HEATER_USERNAME,
            HEATER_PASSWORD)
    except Exception:
        return False
    return True


def stop_flame():
    try:
        cmds.pl_switch(
            HEATER_PROTOCOL,
            HEATER_DID,
            "off",
            HEATER_API,
            HEATER_USERNAME,
            HEATER_PASSWORD)
    except Exception:
        return False
    return True


def get_temp(metaObj):
    return requests.get(INT_TEMP_URL).json()["temperature"]



