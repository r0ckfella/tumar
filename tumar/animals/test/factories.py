import datetime
import random
from decimal import Decimal

import factory.fuzzy
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point, GeometryCollection, Polygon
from django.utils import timezone as tz
from faker import Factory as FakerFactory
from pytz import timezone

from ..models import Farm, Animal, Geolocation, Event, Machinery
from ...users.test.factories import UserFactory

User = get_user_model()
faker = FakerFactory.create()


# faker.seed_instance(4321)


class FarmFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Farm
        django_get_or_create = ('iin',)

    id = factory.Faker('uuid4')
    user = factory.Iterator(User.objects.all())
    iin = factory.Faker('numerify', text="#############")
    legal_person = factory.Faker('name')
    requisites = ''
    breeding_stock = factory.Faker('random_int', min=0, max=9999, step=1)
    calves_number = factory.Faker('random_int', min=0, max=9999, step=1)

    # cadastres = factory.List([factory.Faker('numerify', text="#############") for _ in range(random.randrange(1, 5))])

    # @factory.lazy_attribute
    # def cadastre_land(self):
    #     polygons = GeometryCollection(srid=4326)
    #
    #     for _ in range(len(self.cadastres)):
    #         center_lat = faker.coordinate(center=Decimal('52.005850'), radius=0.2)
    #         center_lon = faker.coordinate(center=Decimal('67.821587'), radius=0.4)
    #         num_of_points = random.randrange(8, 15)
    #
    #         temp_polygon = [(float(faker.coordinate(center=center_lon, radius=0.004)),
    #                          float(faker.coordinate(center=center_lat, radius=0.002))) for _ in
    #                         range(num_of_points)]
    #
    #         temp_polygon.append(temp_polygon[0])
    #         polygons.append(Polygon(temp_polygon, srid=4326).convex_hull)
    #
    #     return polygons


class AnimalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Animal
        django_get_or_create = ('tag_number', 'imei',)

    id = factory.Faker('uuid4')
    farm = factory.Iterator(Farm.objects.all())
    imei = factory.Faker('numerify', text="###############")
    tag_number = factory.Faker('numerify', text="############")
    imsi = factory.Faker('numerify', text="##################")
    battery_charge = factory.Faker('random_int', min=1, max=99, step=1)
    updated = factory.Faker('date_time_between',
                            tzinfo=timezone('Asia/Almaty'),
                            end_date=datetime.datetime.now(),
                            start_date=datetime.datetime.now() - datetime.timedelta(days=2))

    @factory.lazy_attribute
    def name(self):
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

    @factory.lazy_attribute
    def time(self):
        time = faker.date_time_between(
            tzinfo=timezone('Asia/Almaty'),
            end_date="now",
            start_date=datetime.datetime(2019, 12, 1,
                                         tzinfo=timezone('Asia/Almaty')))
        time = time.replace(minute=0, second=0)
        return time

    @factory.lazy_attribute
    def position(self):
        lon = faker.coordinate(center=Decimal('67.821587'), radius=0.4)
        lat = faker.coordinate(center=Decimal('52.005850'), radius=0.2)
        return Point(float(lon), float(lat), srid=4326)

    class Params:
        parents = factory.Trait(
            animal=factory.SubFactory(AnimalFactory),
        )


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event

    animal = factory.Iterator(Animal.objects.all())
    time = factory.Faker('date_time_between',
                         tzinfo=timezone('Asia/Almaty'),
                         end_date=datetime.datetime.now() + datetime.timedelta(days=120),
                         start_date=datetime.datetime(2016, 1, 1,
                                                      tzinfo=timezone('Asia/Almaty')))
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)

    @factory.lazy_attribute
    def completed(self):
        if self.time > tz.now():
            return False

        return faker.boolean(chance_of_getting_true=95)


class MachineryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Machinery
        django_get_or_create = ('machinery_code',)

    id = factory.Faker('uuid4')
    farm = factory.Iterator(Farm.objects.all())
    machinery_code = factory.Faker('hexify', text="^^^^^^^^^^^^^^^", upper=False)

    @factory.lazy_attribute
    def type(self):
        species = ['tractor', 'cultivator', 'cultipacker', 'harrow', 'subspoiler', 'roller', 'strip till', 'seed drill',
                   'planter', 'manure spreader', 'sprayer', 'grain cart', 'combiner', 'harvester', 'baler', 'swather']

        return random.choice(species)

    class Params:
        parents = factory.Trait(
            farm=factory.SubFactory(FarmFactory),
        )
