"""Factories for the aps_bom app."""
from decimal import Decimal

from django.utils.timezone import now

import factory

from ..models import (
    AdditionalText,
    BOM,
    BOMItem,
    CBOM,
    CBOMItem,
    Company,
    Country,
    EPN,
    IPN,
    PriceGroup,
    PriceMarker,
    Shape,
    Unit,
)


class AdditionalTextFactory(factory.DjangoModelFactory):
    """Factory for the ``AdditionalText`` model."""
    FACTORY_FOR = AdditionalText

    ipn = factory.SubFactory('aps_bom.tests.factories.IPNFactory')
    text = factory.Sequence(lambda n: 'text {0}'.format(n))


class BOMFactory(factory.DjangoModelFactory):
    """Factory for the ``BOM`` model."""
    FACTORY_FOR = BOM

    description = factory.Sequence(lambda n: 'description {0}'.format(n))
    ipn = factory.SubFactory('aps_bom.tests.factories.IPNFactory')


class BOMItemFactory(factory.DjangoModelFactory):
    """Factory for the ``BOMItem`` model."""
    FACTORY_FOR = BOMItem

    bom = factory.SubFactory(BOMFactory)
    ipn = factory.SubFactory('aps_bom.tests.factories.IPNFactory')
    position = factory.Sequence(lambda n: '{0}'.format(n))
    qty = factory.Sequence(lambda n: n)
    unit = factory.SubFactory('aps_bom.tests.factories.UnitFactory')


class CBOMFactory(factory.DjangoModelFactory):
    """Factory for the ``CBOM`` model."""
    FACTORY_FOR = CBOM

    customer = factory.SubFactory('aps_bom.tests.factories.CompanyFactory')
    description = factory.Sequence(lambda n: 'description {0}'.format(n))
    html_link = factory.Sequence(lambda n: 'http://example.com/{0}/'.format(n))
    product = factory.Sequence(lambda n: 'product {0}'.format(n))
    version_date = now()


class CBOMItemFactory(factory.DjangoModelFactory):
    """Factory for the ``CBOMItem`` model."""
    FACTORY_FOR = CBOMItem

    bom = factory.SubFactory(CBOMFactory)
    epn = factory.SubFactory('aps_bom.tests.factories.EPNFactory')
    position = factory.Sequence(lambda n: '{0}'.format(n))
    qty = factory.Sequence(lambda n: n)
    unit = factory.SubFactory('aps_bom.tests.factories.UnitFactory')


class CompanyFactory(factory.DjangoModelFactory):
    """Factory for the ``Company`` model."""
    FACTORY_FOR = Company

    country = factory.SubFactory('aps_bom.tests.factories.CountryFactory')
    code = factory.Sequence(lambda n: 'code {0}'.format(n))
    description = factory.Sequence(lambda n: 'description {0}'.format(n))


class CountryFactory(factory.DjangoModelFactory):
    """Factory for the ``Country`` model."""
    FACTORY_FOR = Country

    code = 'de'
    description = factory.Sequence(lambda n: 'description {0}'.format(n))


class EPNFactory(factory.DjangoModelFactory):
    """Factory for the ``EPN`` model."""
    FACTORY_FOR = EPN

    company = factory.SubFactory(CompanyFactory)
    cpn = factory.SubFactory('aps_bom.tests.factories.IPNFactory')
    description = factory.Sequence(lambda n: 'description {0}'.format(n))
    epn = factory.Sequence(lambda n: 'epn {0}'.format(n))
    ipn = factory.SubFactory('aps_bom.tests.factories.IPNFactory')


class IPNFactory(factory.DjangoModelFactory):
    """Factory for the ``IPN`` model."""
    FACTORY_FOR = IPN

    code = factory.Sequence(lambda n: 'code {0}'.format(n))
    name = factory.Sequence(lambda n: 'name {0}'.format(n))
    price_group = factory.SubFactory(
        'aps_bom.tests.factories.PriceGroupFactory')
    shape = factory.SubFactory('aps_bom.tests.factories.ShapeFactory')
    price_max = Decimal('123.45')


class PriceGroupFactory(factory.DjangoModelFactory):
    """Factory for the ``PriceGroup`` model."""
    FACTORY_FOR = PriceGroup

    code = 'A'


class PriceMarkerFactory(factory.DjangoModelFactory):
    """Factory for the ``PriceMarker`` model."""
    FACTORY_FOR = PriceMarker

    ipn = factory.SubFactory(IPNFactory)
    price = Decimal('54.321')
    date = now()


class ShapeFactory(factory.DjangoModelFactory):
    """Factory for the ``Shape`` model."""
    FACTORY_FOR = Shape

    code = factory.Sequence(lambda n: 'code {0}'.format(n))
    name = factory.Sequence(lambda n: 'name {0}'.format(n))


class UnitFactory(factory.DjangoModelFactory):
    """Factory for the ``Unit`` model."""
    FACTORY_FOR = Unit

    code = factory.Sequence(lambda n: 'c{0}'.format(n))
    description = factory.Sequence(lambda n: 'description {0}'.format(n))
