from django.db import models

from django.utils import timezone

STATUS_PUBLISHED = 0


class AdvertisementManager(models.Manager):
    """ Manager for advertisements. """

    def by_advertiser(advertiser):
        """ Gets all advertisments from the given advertiser. """
        return self.get_queryset().filter(advertiser=advertiser)

    def published():
        """ Gets all published advertisements. """
        now = timezone.now()
        return self.get_queryset().filter(
            status=STATUS_PUBLISHED, publish_on__gte=now, publish_until__lte=now)