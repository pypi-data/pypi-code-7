import logging
from django.conf import settings


class Logger():

    @staticmethod
    def getLogger():

        logger = logging.getLogger("thermostat.rules")
        logger.setLevel(settings.LOG_LEVEL)
        return logger
