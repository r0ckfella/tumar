import datetime
from decimal import Decimal

import factory.fuzzy
import random

from django.contrib.gis.geos import Point
from faker import Factory as FakerFactory
from pytz import timezone

from ..models import Farm, Animal, Geolocation

faker = FakerFactory.create()


class FarmFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Farm
        django_get_or_create = ('name', 'key')

    id = factory.Faker('uuid4')
    key = factory.Faker('hexify', text="^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", upper=False)
    name = factory.Faker('company')


class AnimalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Animal
        django_get_or_create = ('cow_code', 'imei',)

    id = factory.Faker('uuid4')
    farm = factory.Iterator(Farm.objects.all())
    imei = factory.Faker('numerify', text="###############")

    @factory.lazy_attribute
    def cow_code(self):
        species = ['Cow', 'Horse', 'Sheep']
        return random.choice(species) + " " + faker.first_name()

    class Params:
        parents = factory.Trait(
            farm=factory.SubFactory(FarmFactory),
        )


class GeolocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Geolocation

    animal = factory.Iterator(Animal.objects.all())
    time = factory.Faker('date_time_between',
                         tzinfo=timezone('Asia/Almaty'),
                         end_date="now",
                         start_date=datetime.datetime(2016, 1, 1,
                                                      tzinfo=timezone('Asia/Almaty')))

    @factory.lazy_attribute
    def position(self):
        lat = faker.coordinate(center=Decimal('52.005850'), radius=0.2)
        lon = faker.coordinate(center=Decimal('67.821587'), radius=0.4)
        return Point(float(lon), float(lat), srid=4326)

    class Params:
        parents = factory.Trait(
            animal=factory.SubFactory(AnimalFactory),
        )
