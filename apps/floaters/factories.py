import factory
from .models import Floaters

class FloaterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Floaters

    display_name = factory.Sequence(lambda n: f'Floater {n}')
    display_description = factory.Faker('paragraph')
    display_order = factory.Sequence(lambda n: n)
    short_description = factory.Faker('sentence')
    tier = Floaters.STARTER_PACK
