import requests
from django.conf import settings
from hautomation_restclient.cmds import pl_switch
from django_thermostat.models import Context, Thermometer
from django.core.urlresolvers import reverse
from time import strftime, localtime, mktime, strptime
import os, logging, simplejson

logger = logging.getLogger("thermostat.rules.mappings")
logger.setLevel(settings.LOG_LEVEL)


def current_external_temperature(mo=None):
    try:

        if not settings.LIST_THERMOMETERS_API is None:
            ret = requests.get("http://localhost%stemperatures=True" % reverse("temperatures"))
            therms = ret.json()
        else:
            therms = simplejson.loads(read_temperatures())

        for therm in therms:
            data = therms[therm]

            if data["is_external"]:
                d = float(data["temp"]["celsius"])
                logger.debug("External temperature: %s" % d)
                return d
        logger.debug("No external thermometer found")
    except Exception as et:
        logger.error(et)


def current_internal_temperature(mo=None):
    try:

        if not settings.LIST_THERMOMETERS_API is None:
            ret = requests.get("http://localhost%stemperatures=True" % reverse("temperatures"))
            therms = ret.json()
        else:
            therms = simplejson.loads(read_temperatures())

        for therm in therms:
            data = therms[therm]
      
            if data["is_internal"]:
                t = float(data["temp"]["celsius"])
                logger.debug("Internal temp: %s" % t)
                return t
        logger.debug("No internal thermometer found")
    except Exception as et:
        logger.error(et)
    

def confort_temperature(mo=None):
    try:
        ctxt = Context.objects.get()

        t = float(ctxt.confort_temperature) + settings.HEATER_MARGIN \
            if ctxt.flame else ctxt.confort_temperature
        logger.debug("Comfort temp: %s" % t)
        return t
    except Exception as et:
        logger.error(et)


def economic_temperature(mo=None):
    try:
        ctxt = Context.objects.get()

        t = float(ctxt.economic_temperature) + settings.HEATER_MARGIN \
            if ctxt.flame else ctxt.economic_temperature
        logger.debug("Economic temp:  %s" % t)
        return t
    except Exception as et:
        logger.error(et)

def tuned_temperature(mo=None):
    try:
        ctxt = Context.objects.get()

        t = float(ctxt.tuned_temperature) + settings.HEATER_MARGIN \
            if ctxt.flame else ctxt.tuned_temperature
        logger.debug("Tunned temp: %s" % t)
        return t
    except Exception as et:
        logger.error(et)

def tune_to_confort(mo=None):
    try:
        ctxt = Context.objects.get()
        ctxt.tuned_temperature = ctxt.confort_temperature
        ctxt.save()
        logger.debug("Tunned to comfort")
    except Exception as et:
        logger.error(et)


def tune_to_economic(mo=None):
    try:

        ctxt = Context.objects.get()

        ctxt.tuned_temperature = ctxt.economic_temperature
        ctxt.save()
        logger.debug("Tunned to economic")
    except Exception as et:
        logger.error(et)
    


def heater_manual(mo=None):
    try:
        r = int(Context.objects.get().manual)
        logger.debug("Heater is set to manual: %s" % r)
        return r
    except Exception as et:
        logger.error(et)


def heater_on(mo=None):
    try:
        r = int(Context.objects.get().heat_on)
        logger.debug("Heater is on: %s" % r)
        return r
    except Exception as et:
        logger.error(et)


def set_heater_on(no=None):
    try:
        ctxt = Context.objects.get()
        ctxt.heat_on = True
        ctxt.save()
        logger.debug("Heater tuner ON")
    except Exception as et:
        logger.error(et)


def set_heater_off(no=None):
    try:
        ctxt = Context.objects.get()
        ctxt.heat_on = False
        ctxt.save()
        logger.debug("Heater turned OFF")
    except Exception as et:
        logger.error(et)

def flame_on():
    try:
        r = 1 if Context.objects.get().flame else 0
        logger.debug("Flamie is on: %s" % r)
        return r
    except Exception as et:
        logger.error(et)

def log_flame_stats(new_state):
    try:
        if settings.FLAME_STATS:
            with open(settings.FLAME_STATS_PATH, "a") as stats:
                t = localtime()
                st = strftime(settings.FLAME_STATS_DATE_FORMAT, t)
                stats.write("%s - %s - %f\n" % (
                    "ON" if new_state else "OFF",
                    st,
                    mktime(strptime(st, settings.FLAME_STATS_DATE_FORMAT))))
    except Exception as et:
        logger.error(et)


def start_flame():

    try:
        ctxt = Context.objects.get()
        if ctxt.flame:
            logger.debug("Not starting flame, because its already started")
            return

        pl_switch(
            settings.HEATER_PROTOCOL,
            settings.HEATER_DID,
            "on",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)

        ctxt.flame = True
        ctxt.save()

        logger.debug("Flame started")
        log_flame_stats(True)
    except Exception as et:
        logger.error(et)

def stop_flame():
    try:
        ctxt = Context.objects.get()
        if not ctxt.flame:
            logger.debug("Not stopping flame, because its already stopped")
            return

        pl_switch(
            settings.HEATER_PROTOCOL,
            settings.HEATER_DID,
            "off",
            settings.HEATER_API,
            settings.HEATER_USERNAME,
            settings.HEATER_PASSWORD)

        ctxt.flame = False
        ctxt.save()

        logger.debug("Flame stopped")
        log_flame_stats(False)
        #print "%s flame stopped" % strftime("%d.%m.%Y %H:%M:%S", localtime())
    except Exception as et:
        logger.error(et)

mappings = [
    current_internal_temperature,
    current_external_temperature,
    confort_temperature,
    economic_temperature,
    start_flame,
    stop_flame,
    heater_manual,
    heater_on,
    flame_on,
    tune_to_confort,
    tune_to_economic,
    tuned_temperature,
    set_heater_off,
    set_heater_on,
    ]
