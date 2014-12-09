# -*- coding:utf-8 -*-

# Stdlib imports

# Core Django imports
from django.db import models
from django.utils.translation import ugettext as _

# Third-party app imports


# Imports from your apps
from .mixins import AddressMixin, CityMixin


class City(CityMixin):
    u"""
    Model to define a info about a city
    """
    pass


class Address(AddressMixin):
    """
    Model to define a address
    """

    city = models.ForeignKey(
        City,
        verbose_name=_(u'City'),
    )
