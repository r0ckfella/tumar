from django.contrib.gis.geos import LineString
from django.db import models


class GeolocationQuerySet(models.QuerySet):
    def get_path(self, animal, start_time, end_time):
        geolocations_qs = self.filter(animal=animal).filter(time__range=(start_time, end_time)).order_by('time')
        the_path = LineString([geolocation.position for geolocation in geolocations_qs], srid=3857)
        return the_path
