from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import Group
from django.contrib.gis import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import Farm, Animal, Geolocation, Machinery, Event
from .utils import download_geolocations


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
        download_geolocations(request)

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


admin.site.site_header = _("Tumar Control Panel")
