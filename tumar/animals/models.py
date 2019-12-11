import uuid

from django.contrib.gis.db import models
from django.core.validators import RegexValidator
from django.db import models as og_models


# Create your models here.

class Farm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=32)
    name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.id + ":" + self.name


class Animal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="animals")
    imei_regex = RegexValidator(regex=r'^\d{15}$',
                                message=("Imei must be entered in the format: '123456789012345'. "
                                         "Up to 15 digits allowed."))
    imei = models.CharField(validators=[imei_regex], max_length=15, null=True, blank=True)
    cow_code = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.imei + ":" + self.cow_code


class Geolocation(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="geolocation")
    position = models.PointField(srid=3857)
    time = models.DateTimeField()

    class Meta:
        unique_together = ('animal', 'position', 'time',)

    def __str__(self):
        return self.animal.imei + " was at " + self.position + " at " + str(self.time)
