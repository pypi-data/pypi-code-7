import logging

from hautomation_restclient.cmds import (
    pl_switch,
    pl_all_lights_off,
    pl_all_lights_on)


from django.conf import settings

logger = logging.getLogger("thermostat.rules.mappings")
logger.setLevel(settings.LOG_LEVEL)


def luz_pasillo_off(mo=None):
    try:
        pl_switch(
            "X10",
            settings.LUZ_PASILLO_DID,
            "off",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Luz del pasillo apagada")
    except Exception as ex:
        logger.error(ex)


def luz_pasillo_on(mo=None):
    try:
        pl_switch(
            "X10",
            settings.LUZ_PASILLO_DID,
            "on",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Luz del pasillo encendida")
    except Exception as ex:
        logger.error(ex)

def salon_on(mo=None):
    try:
        pl_switch(
            "X10",
            settings.SALON_DID,
            "on",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Salon subido")
    except Exception as ex:
        logger.error(ex)


def salon_off(mo=None):
    try:
        pl_switch(
            "X10",
            settings.SALON_DID,
            "off",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Salon bajado")
    except Exception as ex:
        logger.error(ex)


def pasillo_off(mo=None):
    try:
        pl_switch(
            settings.HEATER_PROTOCOL,
            settings.PASILLO_DID,
            "off",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Pasillo bajado")
    except Exception as ex:
        logger.error(ex)


def pasillo_on(mo=None):
    try:
        pl_switch(
            "X10",
            settings.PASILLO_DID,
            "on",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Pasillo subido")
    except Exception as ex:
        logger.error(ex)


def cuarto_oeste_off(mo=None):

    try:
        pl_switch(
            "X10",
            settings.CUARTO_OESTE_DID,
            "off",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Cuarto oeste bajado")
    except Exception as ex:
        logger.error(ex)


def cuarto_oeste_on(mo=None):
    try:
        pl_switch(
            "X10",
            settings.CUARTO_OESTE_DID,
            "on",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Cuarto oeste subido")
    except Exception as ex:
        logger.error(ex)


def cuarto_este_off(mo=None):
    try:
        pl_switch(
            "X10",
            settings.CUARTO_ESTE_DID,
            "off",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Cuarto este bajado")
    except Exception as ex:
        logger.error(ex)

def cuarto_este_on(mo=None):
    try:
        pl_switch(
            "X10",
            settings.CUARTO_ESTE_DID,
            "on",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Cuarto este subido")
    except Exception as ex:
        logger.error(ex)


def a_lights_off(mo=None):
    try:
        pl_all_lights_off(
            "X10",
            "A",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Grupo A bajado")
    except Exception as ex:
        logger.error(ex)


def a_lights_on(mo=None):
    try:
        pl_all_lights_on(
            "X10",
            "A",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)
        logger.debug("Grupo A subido")
    except Exception as ex:
        logger.error(ex)


mappings = [
    salon_off,
    salon_on,
    cuarto_este_on,
    cuarto_este_off,
    cuarto_oeste_off,
    cuarto_oeste_on,
    pasillo_on,
    pasillo_off,
    a_lights_off,
    a_lights_on,
    luz_pasillo_off,
    luz_pasillo_on,
    ]
