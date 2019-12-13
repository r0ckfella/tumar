from django.db import models


class GeolocationQuerySet(models.QuerySet):
    def get_path(self, animal_imei, start_time, end_time):
        return self.filter(animal__imei=animal_imei).filter(time__range=(start_time, end_time)).order_by('time')
