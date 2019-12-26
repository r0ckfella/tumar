import json
from datetime import datetime as dt

import django.utils.timezone as tz
import pytz
import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group
from django.contrib.gis import admin
from django.contrib.gis.geos import Point
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import Farm, Animal, Geolocation, Machinery, Event


class InLineAnimal(admin.TabularInline):
    model = Animal
    extra = 1


@admin.register(Farm)
class FarmAdmin(admin.OSMGeoAdmin):
    inlines = [InLineAnimal]
    default_lat = 6256619
    default_lon = 7470047
    default_zoom = 4
    modifiable = False


@admin.register(Geolocation)
class GeolocationAdmin(admin.OSMGeoAdmin):
    list_display = ('animal', 'time',)
    date_hierarchy = 'time'
    list_filter = ('time', 'animal',)
    default_lat = 6256619
    default_lon = 7470047
    default_zoom = 4
    modifiable = False
    change_list_template = 'admin/animals/geolocation/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('download-geolocations/', self.download_geolocations, name='download_geolocations')
        ]
        return custom_urls + urls

    @method_decorator(staff_member_required)
    def download_geolocations(self, request):
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
                print("New animal is added, and the corresponding location too.")
                the_farm = Farm.objects.get(user=request.user)
                temp_animal = Animal.objects.create(farm=the_farm, imei=location['imei'],
                                                    tag_number=location['cow_code'])
                Geolocation.geolocations.create(animal=temp_animal,
                                                position=Point(float(location['longitude']),
                                                               float(location['latitude']),
                                                               srid=4326),
                                                time=tz.make_aware(my_date, my_tz))

        self.message_user(request, 'Geolocations were just updated.')
        return HttpResponseRedirect("../")

    download_geolocations.short_description = 'Download New Geolocation Data'


@admin.register(Machinery)
class MachineryAdmin(admin.ModelAdmin):
    list_display = ('machinery_code', 'type', 'farm',)
    list_filter = ('type',)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('imei', 'tag_number', 'name', 'farm',)
    list_filter = ('farm',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'time', 'animal',)
    list_filter = ('time', 'completed', 'animal',)
    date_hierarchy = 'time'


admin.site.unregister(Group)

admin.site.site_header = _("Tumar Control Panel")
