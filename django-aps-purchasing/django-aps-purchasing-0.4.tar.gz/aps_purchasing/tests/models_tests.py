"""Tests for the models of the aps_purchasing app."""
from django.test import TestCase

from . import factories


class AMLTestCase(TestCase):
    """Tests for the ``AML`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.AMLFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class CurrencyTestCase(TestCase):
    """Tests for the ``Currency`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.CurrencyFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class DistributorTestCase(TestCase):
    """Tests for the ``Distributor`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.DistributorFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class DPNTestCase(TestCase):
    """Tests for the ``DPN`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.DPNFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class ManufacturerTeEstCase(TestCase):
    """Tests for the ``Manufacturer`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.ManufacturerFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class MPNTestCase(TestCase):
    """Tests for the ``MPN`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.MPNFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class PackagingUnitTestCase(TestCase):
    """Tests for the ``PackagingUnit`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.PackagingUnitFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class PaymentTermTestCase(TestCase):
    """Tests for the ``PaymentTerm`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.PaymentTermFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class PriceTestCase(TestCase):
    """Tests for the ``Price`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.PriceFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class QuotationTestCase(TestCase):
    """Tests for the ``Quotation`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.QuotationFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))


class QuotationItemTestCase(TestCase):
    """Tests for the ``QuotationItem`` model."""
    longMessage = True

    def test_model(self):
        obj = factories.QuotationItemFactory()
        self.assertTrue(obj.pk, msg=(
            'Should be able to create and save instance'))
