from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import Farm, Animal, Geolocation


@admin.register(Geolocation)
class GeolocationAdmin(admin.ModelAdmin):
    date_hierarchy = 'time'
    list_filter = ('time',)


admin.site.register(Farm)
admin.site.register(Animal)
admin.site.unregister(Group)

admin.site.site_header = _("Tumar Control Panel")
