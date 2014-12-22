from models import City, Country
import factory

class CityFactory(factory.DjangoModelFactory):
    FACTORY_FOR = City

    remote_id = factory.Sequence(lambda n: n)

class CountryFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Country

    remote_id = factory.Sequence(lambda n: n)