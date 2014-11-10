from django.core.management.base import BaseCommand, CommandError
from django_thermostat.rules import evaluate
from time import localtime, strftime

import logging
from django.conf import settings


logger = logging.getLogger("thermostat.rules")
logger.setLevel(settings.LOG_LEVEL)


class Command(BaseCommand):
    args = ''
    help = 'Evaluate rules realted to heater status. The result will start or stop the heater'

    def handle(self, *args, **options):
        try:
            logger.info("Starting at %s" % strftime("%d.%m.%Y %H:%M:%S", localtime()))
            evaluate()
            logger.info("Ended at %s" % strftime("%d.%m.%Y %H:%M:%S", localtime()))
        except Exception as ex:
            self.stderr.write("ERROR: %s" % ex)
            logger.error("ERROR: %s" % ex)

