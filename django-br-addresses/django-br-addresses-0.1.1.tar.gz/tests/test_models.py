# -*- coding:utf-8 -*-
from __future__ import unicode_literals

# Python imports

#Core Django imports

import unittest2 as unittest
from django.test import TestCase

#Third-party app imports
from model_mommy import mommy

# Relative apps imports

from django_br_addresses.models import (
    City, Address
)



class CityTest(TestCase):
    """
    Class to test a model City
    """
    def setUp(self):
        """
        Setup a test class
        """
        self.city = mommy.make(City)

    def test_city_create_instance(self):
        """
        Test if instance of the model City was created
        """
        self.assertIsInstance(
            self.city,
            City
        )

    def test_return_unicode_method(self):
        """
        Test the return of method unicode in model City
        """
        self.assertEqual(
            u'{} - {}'.format(self.city.state, self.city.name),
            self.city.__unicode__()
        )


class AddressTest(TestCase):
    """
    Class to test a model Address
    """
    def setUp(self):
        """
        Setup a test class
        """
        self.address = mommy.make(Address)

    def test_addresses_create_instance(self):
        """
        Test if instance of the model Address was created
        """
        self.assertIsInstance(
            self.address,
            Address
        )

    def test_return_unicode_method(self):
        """
        Test the return of method unicode in model Address
        """
        self.assertEqual(
            u'{}, {} - {} , {} , {}'.format(
                self.address.city.state,
                self.address.city.name,
                self.address.street,
                self.address.number,
                self.address.neighborhood,
            ),
            self.address.__unicode__()
        )
