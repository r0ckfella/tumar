from django.db.models import Q
from django_filters import rest_framework as rest_filters

from .models import Geolocation, Animal


class AnimalPathFilter(rest_filters.FilterSet):
    time = rest_filters.DateTimeFromToRangeFilter(field_name='time')
    imei = rest_filters.CharFilter(field_name='animal__imei', required=True)

    class Meta:
        model = Geolocation
        fields = ['imei', 'time', ]


class AnimalNameOrTagNumberFilter(rest_filters.FilterSet):
    search = rest_filters.CharFilter(method='filter_name_or_tag_number')

    class Meta:
        model = Animal
        fields = {
            'search',
        }

    def filter_name_or_tag_number(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(tag_number__icontains=value) | Q(imei__icontains=value)
        )
