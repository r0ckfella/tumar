import datetime
import factory.fuzzy
import random

from django.contrib.gis.geos import Point
from faker import Factory as FakerFactory
from pytz import timezone

faker = FakerFactory.create()


class FarmFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'animals.Farm'

    id = factory.Faker('uuid4')
    key = factory.Faker('hexify', text="^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", upper=False)
    name = factory.Faker('company')


class AnimalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'animals.Animal'

    id = factory.Faker('uuid4')
    farm = factory.SubFactory(FarmFactory)
    imei = factory.Faker('numerify', text="###############")

    @factory.lazy_attribute
    def cow_code(self):
        species = ['Cow', 'Horse', 'Sheep']
        return random.choice(species) + " " + faker.first_name()


class GeolocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'animals.Geolocation'

    animal = factory.SubFactory(AnimalFactory)
    # time = factory.fuzzy.FuzzyDateTime(datetime.datetime(2016, 1, 1, tzinfo=timezone('Asia/Almaty')))
    time = factory.Faker('date_time_between',
                         tzinfo=timezone('Asia/Almaty'),
                         end_date="now",
                         start_date=datetime.datetime(2016, 1, 1,
                                                      tzinfo=timezone('Asia/Almaty')))

    @factory.lazy_attribute
    def position(self):
        lat, lon = faker.local_latlng(country_code="KZ", coords_only=True)
        return Point(float(lon), float(lat), srid=4326)
