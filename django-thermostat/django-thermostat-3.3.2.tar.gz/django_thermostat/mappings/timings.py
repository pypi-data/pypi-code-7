from time import strftime, localtime, mktime, strptime
from astral import Location#, AstralGeocoder
import datetime, logging
from django.conf import settings as settings
import pytz


logger = logging.getLogger("thermostat.rules.mappings")
logger.setLevel(settings.LOG_LEVEL)


def current_day_of_week(mo=None):
    try:
        d = strftime("%a", localtime())
        logger.debug("Current day of week: %s" % d)
        return d
    except Exception as ex:
        logger.error(ex)


def current_month(mo=None):
    try:
        m = strftime("%m", localtime())
        logger.debug("Current month: %s" % m)
        return m
    except Exception as ex:
        logger.error(ex)


def current_year(mo=None):
    try:
        y = strftime("%Y", localtime())
        logger.debug("Current year: %s" % y)
        return y
    except Exception as ex:
        logger.error(ex)


def current_day_of_month(mo=None):
    try:
        d = strftime("%d", localtime())
        logger.debug("Current day of month: %s" % d)
        return d
    except Exception as ex:
        logger.error(ex)


def current_time(mo=None):
    try:
        lt = localtime()
        st = "%s %s %s %s:%s:%s" %(
            strftime("%d", lt),
            strftime("%m", lt),
            strftime("%Y", lt),
            strftime("%H", lt),
            strftime("%M", lt),
            strftime("%S", lt))
        t = strptime(st, "%d %m %Y %H:%M:%S")
        t = mktime(t)
        logger.debug("Current time: %s" % t)
        return t
    except Exception as ex:
        logger.error(ex)



def is_weekend(mo=None):
    try:
        today = current_day_of_week()
        if today == "Sat" or today == "Sun":
            logger.debug("Is not weekend")
            return 1
        logger.debug("Is weekend")
        return 0
    except Exception as ex:
        logger.error(ex)


def is_at_night(mo=None):
    try:
        a = Location()
        a.timezone = settings.TIME_ZONE
        tz = pytz.timezone(a.timezone)
        #Tue, 22 Jul 2008 08:17:41 +0200
        #Sun, 26 Jan 2014 17:39:49 +01:00
        a_sunset = a.sunset()

        a_sunrise = a.sunrise()

        n = datetime.datetime.now()
        n = tz.localize(n)
        logger.debug("NOW: %s; sunrise: %s; dif: %s"  % (n, a_sunrise, n - a_sunrise))
        logger.debug("NOW: %s; sunset: %s; dif: %s" % (n, a_sunset, n - a_sunset))
        passed_sunrise = (n - a_sunrise) > datetime.timedelta(minutes=settings.MINUTES_AFTER_SUNRISE_FOR_DAY)
        logger.debug("Passed %s sunrise more than %s minutes" % (passed_sunrise, settings.MINUTES_AFTER_SUNRISE_FOR_DAY))
        passed_sunset = (n - a_sunset) > datetime.timedelta(minutes=settings.MINUTES_AFTER_SUNSET_FOR_DAY)
        logger.debug("Passed %s sunset more than %s minutes" % (passed_sunset, settings.MINUTES_AFTER_SUNSET_FOR_DAY))

        if not passed_sunrise or passed_sunset:
            logger.debug("Is at night")
            return 1
        if passed_sunrise and not passed_sunset:
            logger.debug("Is not at night")
            return 0
    except Exception as ex:
        logger.error(ex)

mappings = [
    current_day_of_week,
    current_time,
    is_weekend,
    current_month,
    current_day_of_month,
    current_year,
    is_at_night,
    ]
