from models import GroupStat
from vkontakte_groups.factories import GroupFactory
import factory
import random

class GroupStatFactory(factory.DjangoModelFactory):
    FACTORY_FOR = GroupStat

    group = factory.SubFactory(GroupFactory)
    members = factory.LazyAttribute(lambda o: random.randrange(0, 1000))
    visitors = factory.LazyAttribute(lambda o: random.randrange(0, 1000))
