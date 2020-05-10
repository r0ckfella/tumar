from django.contrib.gis import admin

# Register your models here.
from .models import (
    CalfEvent,
    BreedingStockEvent,
    SingleBreedingStockEvent,
    SingleCalfEvent,
)


class SingleBreedingStockEventInline(admin.TabularInline):
    model = SingleBreedingStockEvent
    extra = 1


class SingleCalfEventInline(admin.TabularInline):
    model = SingleCalfEvent
    extra = 1


@admin.register(CalfEvent)
class CalfEventAdmin(admin.ModelAdmin):
    # list_display = ('title', 'time', 'animal',)
    # list_filter = ('time', 'completed', 'animal',)
    # date_hierarchy = 'time'
    inlines = (SingleCalfEventInline,)


@admin.register(BreedingStockEvent)
class BreedingStockEventAdmin(admin.ModelAdmin):
    # list_display = ('title', 'time', 'animal',)
    # list_filter = ('time', 'completed', 'animal',)
    # date_hierarchy = 'time'
    inlines = (SingleBreedingStockEventInline,)
