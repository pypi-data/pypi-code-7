from models import User
import factory
import random

class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    graph_id = factory.Sequence(lambda n: n)
    gender = random.choice(['male','female'])
