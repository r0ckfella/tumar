import uuid

from django.contrib.gis.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


# Create your models here.
from .managers import GeolocationQuerySet


class Farm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    iin = models.CharField(max_length=32, unique=True, verbose_name=_('IIN/BIN'))
    legal_person = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Legal Person'))
    cadastre_num = models.CharField(max_length=25, null=True, blank=True, verbose_name=_('Cadastre Number'))

    class Meta:
        verbose_name = _('Farm')
        verbose_name_plural = _('Farms')

    def __str__(self):
        if self.iin and self.legal_person:
            return self.iin + ":" + self.legal_person
        return self.id


class Animal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="animals", verbose_name=_('farm'))
    imei_regex = RegexValidator(regex=r'^\d{15}$',
                                message=("Imei must be entered in the format: '123456789012345'. "
                                         "Up to 15 digits allowed."))
    imei = models.CharField(validators=[imei_regex], max_length=15, null=True, blank=True, unique=True)
    cow_code = models.CharField(max_length=25, null=True, blank=True, verbose_name=_('Animal ID'), unique=True)

    class Meta:
        verbose_name = _('Animal')
        verbose_name_plural = _('Animals')

    def __str__(self):
        if self.cow_code:
            return self.cow_code
        return self.imei + ":" + self.cow_code


class Geolocation(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="geolocation", verbose_name=_('Animal'))
    position = models.PointField(srid=3857, verbose_name=_('position'))
    time = models.DateTimeField(verbose_name=_('time'))

    geolocations = GeolocationQuerySet.as_manager()

    class Meta:
        unique_together = ('animal', 'time',)
        verbose_name = _('Geo-location')
        verbose_name_plural = _('Geo-locations')

    def __str__(self):
        return str(self.animal.imei) + " was at " + str(self.time)
