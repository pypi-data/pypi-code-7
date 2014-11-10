"""Tests for the models of the aps_bom app."""
import os
from decimal import Decimal

from django.conf import settings
from django.test import TestCase

from ..models import BOM, BOMItem
from .factories import (
    AdditionalTextFactory,
    BOMFactory,
    BOMItemFactory,
    CBOMFactory,
    CBOMItemFactory,
    CompanyFactory,
    CountryFactory,
    EPNFactory,
    IPNFactory,
    PriceGroupFactory,
    PriceMarkerFactory,
    ShapeFactory,
    UnitFactory,
)


class AdditionalTextTestCase(TestCase):
    """Tests for the ``AdditionalText`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``AdditionalText`` model."""
        additionaltext = AdditionalTextFactory()
        self.assertTrue(additionaltext.pk)


class BOMTestCase(TestCase):
    """Tests for the ``BOM`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``BOM`` model."""
        bom = BOMFactory()
        self.assertTrue(bom.pk)


class BOMItemTestCase(TestCase):
    """Tests for the ``BOMItem`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``BOMItem`` model."""
        bomitem = BOMItemFactory()
        self.assertTrue(bomitem.pk)


class CBOMTestCase(TestCase):
    """Tests for the ``CBOM`` model class."""
    longMessage = True

    def setUp(self):
        self.cbom = CBOMFactory()

    def test_instantiation(self):
        """Test instantiation of the ``CBOM`` model."""
        self.assertTrue(self.cbom.pk)

    def test_get_bom(self):
        self.cbomitem = CBOMItemFactory(bom=self.cbom, consign=False)
        self.assertEqual(
            self.cbom.get_bom(),
            BOM(description=self.cbom.description, ipn=None))

    def test_get_bom_csv_file(self):
        path = os.path.join(settings.MEDIA_URL, 'BOM_{0}.csv'.format(
            self.cbom.id))
        self.cbomitem = CBOMItemFactory(bom=self.cbom, consign=False)
        self.assertEqual(self.cbom.get_bom_csv_file(), path)

    def test_get_bom_items(self):
        self.cbomitem = CBOMItemFactory(bom=self.cbom, consign=False)
        CBOMItemFactory(bom=self.cbom, consign=True)
        self.assertEqual(
                self.cbom.get_bom_items()[0],
                BOMItem(ipn=self.cbomitem.epn.ipn,
                        position=self.cbomitem.position,
                        qty=self.cbomitem.qty, unit=self.cbomitem.unit))

    def test_get_csv_file(self):
        path = os.path.join(settings.MEDIA_URL, 'cBOM_{0}.csv'.format(
            self.cbom.id))
        self.cbomitem = CBOMItemFactory(bom=self.cbom, consign=False)
        self.assertEqual(self.cbom.get_csv_file(), path)


class CBOMItemTestCase(TestCase):
    """Tests for the ``CBOMItem`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``CBOMItem`` model."""
        cbomitem = CBOMItemFactory()
        self.assertTrue(cbomitem.pk)


class CompanyTestCase(TestCase):
    """Tests for the ``Company`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Company`` model."""
        company = CompanyFactory()
        self.assertTrue(company.pk)


class CountryTestCase(TestCase):
    """Tests for the ``Country`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Country`` model."""
        country = CountryFactory()
        self.assertTrue(country.pk)


class EPNTestCase(TestCase):
    """Tests for the ``EPN`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``EPN`` model."""
        epn = EPNFactory()
        self.assertTrue(epn.pk)


class IPNTestCase(TestCase):
    """Tests for the ``IPN`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``IPN`` model."""
        ipn = IPNFactory()
        self.assertTrue(ipn.pk)

    def test_price_max(self):
        """Test for the ``price_max`` property."""
        ipn = IPNFactory()
        self.assertIsNone(ipn.price_max, msg=(
            'Without a PriceMarker, the price_max should be None.'))
        PriceMarkerFactory(ipn=ipn)
        self.assertEqual(ipn.price_max, Decimal('54.32100000'), msg=(
            'The price max was not calculated correctly.'))


class PriceGroupTestCase(TestCase):
    """Tests for the ``PriceGroup`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``PriceGroup`` model."""
        pricegroup = PriceGroupFactory()
        self.assertTrue(pricegroup.pk)


class PriceMarkerTestCase(TestCase):
    """Tests for the ``PriceMarker`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``PriceMarker`` model."""
        pricemarker = PriceMarkerFactory()
        self.assertTrue(pricemarker.pk)


class ShapeTestCase(TestCase):
    """Tests for the ``Shape`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Shape`` model."""
        shape = ShapeFactory()
        self.assertTrue(shape.pk)


class UnitTestCase(TestCase):
    """Tests for the ``Unit`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Unit`` model."""
        unit = UnitFactory()
        self.assertTrue(unit.pk)
