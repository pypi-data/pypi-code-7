# -*- coding: utf-8 -*-
"""Factories for the aps_purchasing app."""
from django.utils.timezone import now

import factory

from aps_bom.tests.factories import IPNFactory

from .. import models


class AMLFactory(factory.DjangoModelFactory):
    """Factory for the ``AML`` model."""
    FACTORY_FOR = models.AML

    ipn = factory.SubFactory(IPNFactory)
    manufacturer = factory.SubFactory(
        'aps_purchasing.tests.factories.ManufacturerFactory')


class CurrencyFactory(factory.DjangoModelFactory):
    """Factory for the ``Currency`` model."""
    FACTORY_FOR = models.Currency

    iso_code = factory.Sequence(lambda n: 'IS{0}'.format(n))
    name = factory.Sequence(lambda n: 'Currency {0}'.format(n))
    sign = factory.Sequence(lambda n: '${0}'.format(n))


class DistributorFactory(factory.DjangoModelFactory):
    """Factory for the ``Distributor`` model."""
    FACTORY_FOR = models.Distributor

    min_order_value = 1
    currency = factory.SubFactory(CurrencyFactory)
    payment_terms = factory.SubFactory(
        'aps_purchasing.tests.factories.PaymentTermFactory')


class DPNFactory(factory.DjangoModelFactory):
    """Factory for the ``DPN`` model."""
    FACTORY_FOR = models.DPN

    code = factory.Sequence(lambda n: 'code {0}'.format(n))
    name = factory.Sequence(lambda n: 'name {0}'.format(n))
    distributor = factory.SubFactory(DistributorFactory)
    mpn = factory.SubFactory(
        'aps_purchasing.tests.factories.MPNFactory')


class ManufacturerFactory(factory.DjangoModelFactory):
    """Factory for the ``Manufacturer`` model."""
    FACTORY_FOR = models.Manufacturer

    code = factory.Sequence(lambda n: 'code {0}'.format(n))
    name = factory.Sequence(lambda n: 'name {0}'.format(n))


class MPNFactory(factory.DjangoModelFactory):
    """Factory for the ``MPN`` model."""
    FACTORY_FOR = models.MPN

    manufacturer = factory.SubFactory(ManufacturerFactory)
    pku = 1
    unit = factory.SubFactory(
        'aps_purchasing.tests.factories.PackagingUnitFactory')


class PackagingUnitFactory(factory.DjangoModelFactory):
    """Factory for the ``PackagingUnit`` model."""
    FACTORY_FOR = models.PackagingUnit


class PaymentTermFactory(factory.DjangoModelFactory):
    """Factory for the ``PaymentTerm`` model."""
    FACTORY_FOR = models.PaymentTerm

    code = factory.Sequence(lambda n: 'code {0}'.format(n))
    description = factory.Sequence(lambda n: 'description {0}'.format(n))


class PriceFactory(factory.DjangoModelFactory):
    """Factory for the ``Price`` model."""
    FACTORY_FOR = models.Price

    quotation_item = factory.SubFactory(
        'aps_purchasing.tests.factories.QuotationItemFactory')
    moq = 1
    price = 1
    currency = factory.SubFactory(CurrencyFactory)


class QuotationFactory(factory.DjangoModelFactory):
    """Factory for the ``Quotation`` model."""
    FACTORY_FOR = models.Quotation

    distributor = factory.SubFactory(DistributorFactory)
    ref_number = factory.Sequence(lambda n: 'ref {0}'.format(n))
    issuance_date = factory.LazyAttribute(lambda n: now())
    expiry_date = factory.LazyAttribute(lambda n: now())
    is_completed = False


class QuotationItemFactory(factory.DjangoModelFactory):
    """Factory for the ``QuotationItem`` model."""
    FACTORY_FOR = models.QuotationItem

    quotation = factory.SubFactory(QuotationFactory)
    manufacturer = factory.SubFactory(ManufacturerFactory)
    mpn = factory.SubFactory(MPNFactory)
    min_lead_time = 1
    max_lead_time = 2
