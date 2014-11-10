import requests, logging
from django_thermostat.models import Thermometer
from django_thermostat import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = ''
    help = 'Init database with available thermometers'

    def handle(self, *args, **options):
        logging.debug("Discovering. Sending GET request to %s" % settings.LIST_THERMOMETERS_API)
        ret = requests.get(settings.LIST_THERMOMETERS_API)
        if ret.status_code != 200:
            self.stderr.write("Bad return from REST resource %s: %s" % (
                settings.LIST_THERMOMETERS_API,
                ret.text))

        cont = 0
        for therm in ret.json():
            logging.debug("Adding thermometer %s" % therm)

            t, existed = Thermometer.objects.get_or_create(tid=therm)
            if existed:
                continue
            t.save()
            cont = cont + 1
        logging.info("Discovery finished. Added %d new thermometers" % cont)
