import uuid

from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import RegexValidator
from django.db import connections
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.
from rest_framework.exceptions import ValidationError

from .managers import GeolocationQuerySet


class Farm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name="farm")
    iin = models.CharField(max_length=32, unique=True, verbose_name=_('IIN/BIN'))
    legal_person = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Legal person'))
    requisites = models.CharField(max_length=80, null=True, blank=True, verbose_name=_('Requisites'))
    breeding_stock = models.PositiveIntegerField(blank=True, default=0, verbose_name=_('Breeding stock'))
    calves_number = models.PositiveIntegerField(blank=True, default=0, verbose_name=_('Number of calves'))

    class Meta:
        verbose_name = _('Farm')
        verbose_name_plural = _('Farms')

    def __str__(self):
        if self.iin and self.legal_person:
            return self.iin + ":" + self.legal_person
        return str(self.id)


class Machinery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="machinery", verbose_name=_('Farm'))
    type = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Type of machinery'))
    machinery_code = models.CharField(max_length=50, verbose_name=_('Identification code of the machinery'))

    class Meta:
        verbose_name = _('Machinery')
        verbose_name_plural = _('Machinery')

    def __str__(self):
        if self.machinery_code:
            return self.machinery_code
        return str(self.id)


class Animal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="animals", verbose_name=_('Farm'))
    imei_regex = RegexValidator(regex=r'^\d{15}$',
                                message=("Imei must be entered in the format: '123456789012345'. "
                                         "Up to 15 digits allowed."))
    imei = models.CharField(validators=[imei_regex], max_length=15, null=True, blank=True, unique=True)
    tag_number = models.CharField(max_length=25, null=True, verbose_name=_('Animal tag number'), unique=True)
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('Animal name'))
    updated = models.DateTimeField(default=timezone.now)
    imsi = models.CharField(max_length=30, null=True, blank=True, verbose_name=_('IMSI number'))
    battery_charge = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Battery charge'))

    class Meta:
        verbose_name = _('Animal')
        verbose_name_plural = _('Animals')

    def __str__(self):
        if self.name:
            return self.name
        if self.tag_number:
            return self.tag_number

        return self.imei

    @property
    def status(self):
        return self.updated > timezone.now() - timezone.timedelta(days=1)


class Geolocation(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="geolocations", verbose_name=_('Animal'))
    position = models.PointField(srid=3857, verbose_name=_('Position'))
    time = models.DateTimeField(verbose_name=_('Time'))

    geolocations = GeolocationQuerySet.as_manager()

    class Meta:
        unique_together = ('animal', 'time',)
        verbose_name = _('Geo-location')
        verbose_name_plural = _('Geo-locations')

    def __str__(self):
        return str(self.animal.tag_number) + " was at " + str(self.time)


class Event(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="events", verbose_name=_('Animal'))
    title = models.CharField(max_length=80, verbose_name=_('Title'))
    time = models.DateTimeField(default=timezone.now, verbose_name=_('Time of the event'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    completed = models.BooleanField(default=False, verbose_name=_('Completed?'))

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return str(self.animal.tag_number) + ":" + str(self.title) + " at " + str(self.time)


class Cadastre(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name="cadastres", verbose_name=_('Farm'))
    cadastre_num_regex = RegexValidator(regex=r'^\d+$',
                                        message=("Only digits are allowed for the cadastre number. "
                                                 "Up to 30 digits allowed."))
    cad_number = models.CharField(max_length=30, blank=True, verbose_name=_('Cadastre Number'))
    geom = models.GeometryField(srid=3857, blank=True, null=True, verbose_name=_('Geometry'))
    title = models.CharField(max_length=80, blank=True, verbose_name=_('Title'))

    class Meta:
        verbose_name = _('Cadastre')
        verbose_name_plural = _('Cadastres')

    def __str__(self):
        if self.title:
            return "cad-title:" + str(self.title) + "; farm:" + str(self.farm)
        if self.cad_number:
            return "cad-number:" + str(self.cad_number) + "; farm:" + str(self.farm)
        return "cad-id:" + str(self.id) + "; farm:" + str(self.farm)

    def save(self, *args, **kwargs):
        if self.cad_number and not self.geom:
            with connections['egistic_2'].cursor() as cursor:
                cursor.execute(
                    "SELECT ST_AsText(ST_Transform(geom, 3857)) FROM cadastres_cadastre WHERE kad_nomer = %s",
                    [self.cad_number])
                row = cursor.fetchone()
                self.geom = row[0]
        elif not self.cad_number and not self.geom:
            raise ValidationError('Either cad_number or geom must be sent')
        elif self.cad_number and self.geom:
            raise ValidationError('Do not send cad_number and geom together')

        super().save(*args, **kwargs)  # Call the "real" save() method.
