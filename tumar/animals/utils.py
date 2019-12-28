import json

import django.utils.timezone as tz
import pytz
import requests

from django.contrib.gis.geos import LineString, Point
from datetime import datetime as dt

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
