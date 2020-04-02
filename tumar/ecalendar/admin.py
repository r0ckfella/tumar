from django.contrib.gis import admin

# Register your models here.
from .models import CalfEvent, BreedingStockEvent


@admin.register(CalfEvent)
class CalfEventAdmin(admin.ModelAdmin):
    # list_display = ('title', 'time', 'animal',)
    # list_filter = ('time', 'completed', 'animal',)
    # date_hierarchy = 'time'
    pass


@admin.register(BreedingStockEvent)
class BreedingStockEventAdmin(admin.ModelAdmin):
    # list_display = ('title', 'time', 'animal',)
    # list_filter = ('time', 'completed', 'animal',)
    # date_hierarchy = 'time'
    pass
