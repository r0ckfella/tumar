from django_filters import rest_framework as rest_filters

from .models import Geolocation


class AnimalPathFilter(rest_filters.FilterSet):
    time = rest_filters.DateTimeFromToRangeFilter(field_name='time')
    imei = rest_filters.CharFilter(field_name='animal__imei', required=True)

    class Meta:
        model = Geolocation
        fields = ['imei', 'time', ]
