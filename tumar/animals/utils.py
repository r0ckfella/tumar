import json

import django.utils.timezone as tz
import pytz
import requests

from django.contrib.gis.geos import LineString, Point
from datetime import datetime as dt

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import Distance as d

from .models import Animal, Geolocation, Farm


def get_linestring_from_geolocations(geolocations_qs):
    return LineString([geolocation.position for geolocation in geolocations_qs], srid=3857)


def download_geolocations():
    url = 'http://www.xiaomutong.vip/farm/api/v2/gpsData'
    # url = 'http://185.125.44.211/farm/api/v2/gpsData'
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    payload = {
        "key": "ff8080816d5cb3c0016d65cecef300e1",
        "begintime": "2018-01-01 00:00",
        "endtime": "2019-12-10 23:59",
        "imeis": ""
    }

    r = requests.post(url, data=json.dumps(payload), headers=headers)

    if r.status_code != requests.codes.ok:
        r.raise_for_status()
    geo_history = r.json()

    for location in geo_history['data']:
        my_tz = pytz.timezone('Asia/Almaty')
        my_date = dt.strptime(location['CreateTime'], "%Y-%m-%d %H:%M:%S")

        try:
            temp_animal = Animal.objects.get(imei=location['imei'])
            arguments = dict(animal=temp_animal,
                             position=Point(float(location['longitude']),
                                            float(location['latitude']),
                                            srid=4326),
                             time=tz.make_aware(my_date, my_tz))
            if not Geolocation.geolocations.filter(**arguments).exists():
                Geolocation.geolocations.create(**arguments)
        except Animal.DoesNotExist:
            the_farm = Farm.objects.last()
            temp_animal = Animal.objects.create(farm=the_farm, imei=location['imei'],
                                                tag_number=location['cow_code'])
            Geolocation.geolocations.create(animal=temp_animal,
                                            position=Point(float(location['longitude']),
                                                           float(location['latitude']),
                                                           srid=4326),
                                            time=tz.make_aware(my_date, my_tz))
            print("New animal is added, and the corresponding location too.")


def cluster_geolocations(queryset, zoom_distance, zoom_level):
    groups = []
    animal_group_mapping = dict.fromkeys(queryset.values_list('pk', flat=True))
    starting_animal_pk = next(iter(animal_group_mapping.keys()))
    animal_group_mapping[starting_animal_pk] = 0
    groups.append({starting_animal_pk, })

    for unique_animal_pk in animal_group_mapping.keys():
        if animal_group_mapping[unique_animal_pk] is None:
            groups.append({unique_animal_pk, })
            animal_group_mapping[unique_animal_pk] = len(groups) - 1
            current_animal_group = groups[animal_group_mapping[unique_animal_pk]]
        else:
            current_animal_group = groups[animal_group_mapping[unique_animal_pk]]

        current_point = queryset.get(pk=unique_animal_pk).position
        current_animal_group.update(
            queryset.exclude(pk__in=[pk for group in groups for pk in group])
                    .annotate(distance=Distance('position', current_point))
                    .filter(distance__lte=d(km=zoom_distance[int(zoom_level)][1]))
                    .values_list('pk', flat=True)
        )
        animal_group_mapping.update(
            {pk: animal_group_mapping[unique_animal_pk] for pk in current_animal_group}
        )
    assert len(
        [item for group in groups for item in group]) == queryset.count(), "PKs in groups dublicate in another groups"
    return groups
