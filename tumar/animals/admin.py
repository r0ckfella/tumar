from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.gis import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import (
    Farm,
    Animal,
    Geolocation,
    Cadastre,
    BreedingStock,
    BreedingBull,
    Calf,
    StoreCattle,
)
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
    list_display = (
        "animal",
        "time",
    )
    date_hierarchy = "time"
    list_filter = (
        "time",
        "animal",
    )
    default_lat = 6256619
    default_lon = 7470047
    default_zoom = 4
    modifiable = False
    change_list_template = "admin/animals/geolocation/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "download-geolocations/",
                self.download_geolocations,
                name="download_geolocations",
            )
        ]
        return custom_urls + urls

    @method_decorator(staff_member_required)
    def download_geolocations(self, request):
        farms_attrs = Farm.objects.values_list("id", "api_key")

        for farm in farms_attrs:
            if farm[1]:
                download_geolocations(farm[0], farm[1])

        self.message_user(request, "Geolocations were just updated.")
        return HttpResponseRedirect("../")

    download_geolocations.short_description = "Download New Geolocation Data"


# @admin.register(Machinery)
# class MachineryAdmin(admin.ModelAdmin):
#     list_display = ('machinery_code', 'type', 'farm',)
#     list_filter = ('type',)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = (
        "imei",
        "tag_number",
        "name",
        "farm",
    )
    list_filter = ("farm",)


@admin.register(BreedingStock)
class BreedingStockAdmin(admin.ModelAdmin):
    pass


@admin.register(BreedingBull)
class BreedingBullAdmin(admin.ModelAdmin):
    pass


@admin.register(Calf)
class CalfAdmin(admin.ModelAdmin):
    pass


@admin.register(StoreCattle)
class StoreCattleAdmin(admin.ModelAdmin):
    pass


@admin.register(Cadastre)
class CadastreAdmin(admin.ModelAdmin):
    pass


admin.site.site_header = _("Tumar Control Panel")
