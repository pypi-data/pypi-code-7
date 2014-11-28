"""Factories for the aps_production app."""
from django.utils.timezone import now

import factory

from .. import models


class ErrorFactory(factory.DjangoModelFactory):
    """Factory for the ``Error`` model class."""
    FACTORY_FOR = models.Error

    order_run = factory.SubFactory(
        'aps_production.tests.factories.OrderRunFactory')
    error_bin = factory.SubFactory(
        'aps_production.tests.factories.ErrorBinFactory')
    quantity = 1


class ErrorBinFactory(factory.DjangoModelFactory):
    """Factory for the ``ErrorBin`` model class."""
    FACTORY_FOR = models.ErrorBin

    technology = factory.SubFactory(
        'aps_bom.tests.factories.TechnologyFactory')
    error_code = factory.Sequence(lambda n: 'error_code {0}'.format(n))


class OrderFactory(factory.DjangoModelFactory):
    """Factory for the ``Order`` model class."""
    FACTORY_FOR = models.Order

    order_number = factory.Sequence(lambda n: '000{0}'.format(n))
    company = factory.SubFactory(
        'aps_bom.tests.factories.CompanyFactory')
    customer_po_number = factory.Sequence(
        lambda n: 'customer_po_number {0}'.format(n))
    customer_po_date = now()


class OrderLineFactory(factory.DjangoModelFactory):
    """Factory for the ``OrderLine`` model class."""
    FACTORY_FOR = models.OrderLine

    order = factory.SubFactory(OrderFactory)
    line_no = factory.Sequence(lambda n: '{0}'.format(n * 10))
    product = factory.SubFactory('aps_bom.tests.factories.ProductFactory')
    quantity_ordered = 1000
    date_requested = now()


class OrderRunFactory(factory.DjangoModelFactory):
    """Factory for the ``OrderRun`` model class."""
    FACTORY_FOR = models.OrderRun

    order_line = factory.SubFactory(OrderLineFactory)
    run_number = factory.Sequence(lambda n: '{0}'.format(n))
    ipn = factory.SubFactory('aps_bom.tests.factories.IPNFactory')
    quantity_started = 1000
    quantity_dest_out = 10
    quantity_out = 990


class ShipmentFactory(factory.DjangoModelFactory):
    """Factory for the ``Shipment`` model class."""
    FACTORY_FOR = models.Shipment

    order_run = factory.SubFactory(OrderRunFactory)
    quantity = 990
    date_shipped = now()
