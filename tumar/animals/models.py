import uuid
import requests
import json
import datetime

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Area, Cast
from django.db.models import (
    OuterRef,
    Subquery,
    Sum,
    FloatField,
    Avg,
    F,
    ExpressionWrapper,
    Value,
    DateField,
    CharField,
    Count,
)
from django.db.models.functions import ExtractDay, Coalesce
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.
from rest_framework.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

from ..users.utils import compress
from .managers import GeolocationQuerySet
from ..ecalendar.models import SingleCalfEvent, SingleBreedingStockEvent


class Farm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name="farm",
    )
    iin = models.CharField(max_length=32, unique=True, verbose_name=_("IIN/BIN"))
    legal_person = models.CharField(
        max_length=50, blank=True, verbose_name=_("Legal person")
    )
    iik = models.CharField(max_length=80, blank=True, verbose_name=_("IIK"))
    bank = models.CharField(max_length=80, blank=True, verbose_name=_("BANK"))
    bin = models.CharField(max_length=80, blank=True, verbose_name=_("BIN"))
    address = models.CharField(max_length=100, blank=True, verbose_name=_("Address"))
    api_key = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Chinese API key"),
        help_text="Переводит ваш логин в другой формат для быстрого использования"
        + " (к примеру, kh001 в ff80808170c314600170c393dace234)",
    )

    @property
    def calf_count(self):
        return self.calf_set.filter(active=True).count()

    @property
    def breedingstock_count(self):
        return self.breedingstock_set.count()

    @property
    def breedingbull_count(self):
        return self.breedingbull_set.count()

    @property
    def storecattle_count(self):
        return self.storecattle_set.count()

    @property
    def animal_count(self):
        return self.animal_set.count()

    @property
    def total_animal_count(self):
        return (
            self.calf_count
            + self.breedingstock_count
            + self.breedingbull_count
            + self.storecattle_count
            + self.animal_count
        )

    @property
    def total_pastures_area_in_ha(self):
        total_pastures_area = self.cadastres.annotate(area=Area("geom")).aggregate(
            total_area=Sum("area")
        )["total_area"]
        return total_pastures_area.sq_m / 10000

    class Meta:
        verbose_name = _("Farm")
        verbose_name_plural = _("Farms")

    def has_free_request(self):
        return (
            self.cadastres.annotate(ir_count=Count("imagery_requests__pk")).aggregate(
                total_count=Sum("ir_count")
            )["total_count"]
            <= 3
        )

    def __str__(self):
        if self.iin and self.legal_person:
            return self.iin + ":" + self.legal_person
        return str(self.id)

    def save(self, *args, **kwargs):
        if self.api_key and len(self.api_key) != 32:
            url = settings.CHINESE_LOGIN_URL
            headers = {"Content-type": "application/json", "Accept": "application/json"}
            payload = {
                "username": self.api_key,
                "password": settings.STANDARD_LOGIN_PASSWORD,
            }

            r = requests.post(url, data=json.dumps(payload), headers=headers)

            if r.status_code != requests.codes.ok:
                r.raise_for_status()
            response_data = r.json()
            self.api_key = response_data["data"]["cowfarmList"][0]["id"]
        super(Farm, self).save(*args, **kwargs)  # Call the "real" save() method.


class Machinery(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="machinery", verbose_name=_("Farm")
    )
    type = models.CharField(
        max_length=50, blank=True, verbose_name=_("Type of machinery")
    )
    machinery_code = models.CharField(
        max_length=50, verbose_name=_("Identification code of the machinery")
    )

    class Meta:
        verbose_name = _("Machinery")
        verbose_name_plural = _("Machinery")

    def __str__(self):
        if self.machinery_code:
            return self.machinery_code
        return str(self.id)


class BaseAnimal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, verbose_name=_("Farm"))
    tag_number = models.CharField(
        max_length=25, null=True, verbose_name=_("Animal tag number"), unique=True
    )
    name = models.CharField(max_length=30, blank=True, verbose_name=_("Animal name"))
    birth_date = models.DateField(null=True, verbose_name=_("Date of birth"))
    image = models.ImageField(
        upload_to="animalimages",
        max_length=150,
        null=True,
        blank=True,
        verbose_name=_("Photo of the animal"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        if self.name:
            return self.name
        if self.tag_number:
            return self.tag_number

        return self.id

    def save(self, *args, **kwargs):
        if self.image:
            # call the compress function
            new_image = compress(self.image)

            # set self.image to new_image
            self.image = new_image

        super().save(*args, **kwargs)


class Animal(BaseAnimal):
    imei_regex = RegexValidator(
        regex=r"^\d{15}$",
        message=(
            "Imei must be entered in the format: '123456789012345'. "
            "Up to 15 digits allowed."
        ),
    )
    imei = models.CharField(
        validators=[imei_regex],
        max_length=15,
        blank=True,
        unique=True,
        verbose_name=_("IMEI of the tracker"),
    )
    imsi = models.CharField(max_length=30, blank=True, verbose_name=_("IMSI number"))
    battery_charge = models.DecimalField(
        null=True,
        blank=True,
        max_digits=6,
        decimal_places=3,
        verbose_name=_("Battery charge"),
    )
    updated = models.DateTimeField(default=timezone.now, verbose_name=_("Last updated"))

    class Meta:
        verbose_name = _("Animal")
        verbose_name_plural = _("Animals")

    @property
    def status(self):
        return self.updated > timezone.now() - timezone.timedelta(days=1)


KAZ_LH = "KL"
GEREFORD = "GF"
ANGUS = "AG"
KALMYK = "KM"
AULIYEKOL = "AK"
SIMMENTAL = "SM"
MILK_BREED = "MB"
NO_BREED = "NB"
CROSS = "CR"
OTHER = "OT"

BREED_CHOICES = [
    (KAZ_LH, _("Казахская белоголовая")),
    (GEREFORD, _("Герефорд")),
    (ANGUS, _("Ангус")),
    (KALMYK, _("Калмыцкая")),
    (AULIYEKOL, _("Аулиекольская")),
    (SIMMENTAL, _("Симментал")),
    (MILK_BREED, _("Молочные породы")),
    (NO_BREED, _("Беспородная")),
    (CROSS, _("Кросс")),
    (OTHER, _("Другое")),
]


class BreedingStockManager(models.Manager):
    def pregnant_count(self):
        return (
            self.get_queryset()
            .filter(
                events__title__icontains="случка",
                singlebreedingstockevent__completed=False,
            )
            .count()
        )

    def avg_cow_skt(self):
        cow_skt_event = SingleBreedingStockEvent.objects.filter(
            event__title__icontains="СКТ", completed=True, attributes__has_key="skt"
        ).filter(animal=OuterRef("pk"))
        cow_skt_event_query = Subquery(cow_skt_event.values("attributes__skt")[:1])

        avg_cow_skt = (
            self.get_queryset()
            .annotate(skt=Cast(cow_skt_event_query, output_field=CharField()))
            .exclude(skt__isnull=True)
            .annotate(skt_float=Cast("skt", output_field=FloatField()))
            .aggregate(result=Avg("skt_float"))["result"]
        )

        if not avg_cow_skt:
            avg_cow_skt = 0.0

        return avg_cow_skt

    def get_cows_count_by_year(self, years_old):
        curr_year = datetime.datetime.now().year

        cows_count = (
            self.get_queryset()
            .filter(birth_date__year=str(curr_year - years_old))
            .count()
        )

        return cows_count

    def get_cows_count_by_year_range(self, years_old_lower, years_old_upper):
        curr_year = datetime.datetime.now().year

        cows_count = (
            self.get_queryset()
            .filter(
                birth_date__year__range=(
                    curr_year - years_old_upper,
                    curr_year - years_old_lower,
                )
            )
            .count()
        )

        return cows_count


class BreedingStock(BaseAnimal):  # Маточное поголовье
    breed = models.CharField(
        max_length=2,
        choices=BREED_CHOICES,
        default=NO_BREED,
        verbose_name=_("Breed of the animal"),
    )

    class Meta:
        verbose_name = _("Breeding Stock")
        verbose_name_plural = _("Breeding Stock")

    objects = BreedingStockManager()


MALE = "ML"
FEMALE = "FM"

GENDER_CHOICES = [(MALE, _("Бычок")), (FEMALE, _("Телочка"))]


class CalfManager(models.Manager):
    def less_12_months_count(self):
        time_threshold = datetime.date.today() - relativedelta(months=12)
        return (
            self.get_queryset()
            .filter(active=True)
            .filter(birth_date__gt=time_threshold)
            .count()
        )

    def females(self):
        return self.get_queryset().filter(active=True, gender=FEMALE)

    def males(self):
        return self.get_queryset().filter(active=True, gender=MALE)

    def greater_12_months_count(self):
        time_threshold = datetime.date.today() - relativedelta(months=12)
        return (
            self.get_queryset()
            .filter(active=True)
            .filter(birth_date__lt=time_threshold)
            .count()
        )

    def sum_birth_weight(self):
        birth_event = (
            SingleCalfEvent.objects.filter(
                event__title__icontains="отел",
                completed=True,
                attributes__has_key="birth_weight",
            )
            .filter(animal=OuterRef("pk"))
            .order_by("completion_date")
        )
        birth_event_query = Subquery(birth_event.values("attributes__birth_weight")[:1])

        sum_birth_weight = (
            self.get_queryset()
            .filter(active=True)
            .annotate(
                birth_weight_json=Cast(birth_event_query, output_field=CharField())
            )
            .exclude(birth_weight_json__isnull=True)
            .annotate(
                birth_weight_float=Cast("birth_weight_json", output_field=FloatField())
            )
            .aggregate(total_sum=Sum("birth_weight_float"))["total_sum"]
        )

        return sum_birth_weight

    def avg_205_day_predicted_weight(self):
        birth_event = (
            SingleCalfEvent.objects.filter(
                event__title__icontains="отел",
                completed=True,
                attributes__has_key="birth_weight",
            )
            .filter(animal=OuterRef("pk"))
            .order_by("completion_date")
        )
        birth_weight_query = Subquery(
            birth_event.values("attributes__birth_weight")[:1]
        )

        wean_event = (
            SingleCalfEvent.objects.filter(
                event__title__icontains="отъём",
                completed=True,
                attributes__has_key="wean_weight",
            )
            .filter(animal=OuterRef("pk"))
            .order_by("completion_date")
        )
        wean_weight_query = Subquery(wean_event.values("attributes__wean_weight")[:1])
        wean_date_query = Subquery(wean_event.values("completion_date")[:1])

        avg_205_day_weight_formula = ExpressionWrapper(
            ((F("wean_weight_float") - F("birth_weight_float")) * Value(205.0))
            / F("wean_age")
            + F("birth_weight_float"),
            output_field=FloatField(),
        )

        avg_205_day_predicted_weight = (
            self.get_queryset()
            .filter(active=True)
            .annotate(
                birth_weight_json=Cast(birth_weight_query, output_field=CharField())
            )
            .exclude(birth_weight_json__isnull=True)
            .annotate(
                birth_weight_float=Cast("birth_weight_json", output_field=FloatField())
            )
            .annotate(wean_weight=Cast(wean_weight_query, output_field=CharField()))
            .exclude(wean_weight__isnull=True)
            .annotate(wean_weight_float=Cast("wean_weight", output_field=FloatField()))
            .annotate(
                wean_event_date=Cast(
                    Coalesce(
                        wean_date_query, "birth_date"
                    ),  # Coalesce validation for None values
                    output_field=DateField(),
                )
            )
            .annotate(
                wean_age=Cast(
                    ExtractDay(F("wean_event_date") - F("birth_date")) + Value(1),
                    output_field=FloatField(),
                )
            )
            .annotate(predicted_weight=avg_205_day_weight_formula)
            .aggregate(result=Avg("predicted_weight"))["result"]
        )

        if not avg_205_day_predicted_weight:
            avg_205_day_predicted_weight = 0

        return avg_205_day_predicted_weight

    def cows_effectiveness(self):
        day_205_event = (
            SingleCalfEvent.objects.filter(
                event__title__icontains="взвешивание",
                completed=True,
                attributes__has_key="weight",
            )
            .annotate(
                age_int=ExtractDay(F("completion_date") - F("animal__birth_date"))
                + Value(1)
            )
            .filter(age_int__range=(200, 210))
            .filter(animal=OuterRef("pk"))
        )
        day_205_event_query = Subquery(day_205_event.values("attributes__weight")[:1])

        birth_event = SingleBreedingStockEvent.objects.filter(
            event__title__icontains="отел",
            completed=True,
            attributes__has_key="before_weight",
        ).filter(animal=OuterRef("mother"))
        birth_event_query = Subquery(
            birth_event.values("attributes__before_weight")[:1]
        )

        cow_effectiveness_formula = ExpressionWrapper(
            F("day_205_weight_float") / F("before_weight_float"),
            output_field=FloatField(),
        )

        cows_effectiveness = (
            self.get_queryset()
            .filter(active=True)
            .annotate(
                day_205_weight=Cast(day_205_event_query, output_field=CharField(),)
            )
            .exclude(day_205_weight__isnull=True)
            .annotate(
                day_205_weight_float=Cast("day_205_weight", output_field=FloatField())
            )
            .annotate(before_weight=Cast(birth_event_query, output_field=CharField()))
            .exclude(before_weight__isnull=True)
            .annotate(
                before_weight_float=Cast("before_weight", output_field=FloatField())
            )
            .annotate(single_effectiveness=cow_effectiveness_formula)
            .aggregate(result=Avg("single_effectiveness"))["result"]
        )

        if cows_effectiveness is None:
            cows_effectiveness = 0

        return cows_effectiveness * 100


class Calf(BaseAnimal):  # Телята
    wean_date = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Date of weaning")
    )
    gender = models.CharField(
        max_length=2, choices=GENDER_CHOICES, default=FEMALE, verbose_name=_("Gender")
    )
    breed = models.CharField(
        max_length=2,
        choices=BREED_CHOICES,
        default=NO_BREED,
        verbose_name=_("Breed of the animal"),
    )
    mother = models.ForeignKey(
        BreedingStock,
        on_delete=models.CASCADE,
        related_name="calves",
        verbose_name=_("Mother"),
    )
    active = models.BooleanField(default=True, verbose_name=_("Active?"))

    @property
    def birth_weight(self):
        return (
            self.singlecalfevent_set.filter(
                event__title__icontains="отел", completed=True
            )
            .order_by("completion_date")
            .first()
            .event.attributes.get("birth_weight", None)
        )

    class Meta:
        verbose_name = _("Calf")
        verbose_name_plural = _("Calves")

    objects = CalfManager()


class BreedingBullManager(models.Manager):
    pass


class BreedingBull(BaseAnimal):  # Племенной бык
    birth_place = models.CharField(
        max_length=100, blank=True, verbose_name=_("Birth Place")
    )
    breed = models.CharField(
        max_length=2,
        choices=BREED_CHOICES,
        default=NO_BREED,
        verbose_name=_("Breed of the animal"),
    )

    class Meta:
        verbose_name = _("Breeding Bull")
        verbose_name_plural = _("Breeding Bulls")

    objects = BreedingBullManager()


class StoreCattle(BaseAnimal):  # Скот на откорме
    wean_date = models.DateTimeField(
        default=timezone.now, verbose_name=_("Date of weaning")
    )

    class Meta:
        verbose_name = _("Store Cattle")
        verbose_name_plural = _("Store Cattle")


class Geolocation(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name="geolocations",
        verbose_name=_("Animal"),
    )
    position = models.PointField(srid=3857, verbose_name=_("Position"))
    time = models.DateTimeField(verbose_name=_("Time"))

    geolocations = GeolocationQuerySet.as_manager()

    class Meta:
        unique_together = (
            "animal",
            "time",
        )
        verbose_name = _("Geo-location")
        verbose_name_plural = _("Geo-locations")

    def __str__(self):
        return str(self.animal.tag_number) + " was at " + str(self.time)


class Cadastre(models.Model):
    cadastre_num_regex = RegexValidator(
        regex=r"^\d+$",
        message=(
            "Only digits are allowed for the cadastre number. "
            "Up to 30 digits allowed."
        ),
    )

    farm = models.ForeignKey(
        Farm, on_delete=models.CASCADE, related_name="cadastres", verbose_name=_("Farm")
    )
    cad_number = models.CharField(
        max_length=30, blank=True, verbose_name=_("Cadastre Number")
    )
    geom = models.GeometryField(
        srid=3857, blank=True, null=True, verbose_name=_("Geometry")
    )
    title = models.CharField(max_length=80, blank=True, verbose_name=_("Title"))

    class Meta:
        verbose_name = _("Cadastre")
        verbose_name_plural = _("Cadastres")

    @property
    def area(self):
        return f"{self.geom.area / 10000} га"

    def __str__(self):
        if self.title:
            return "cad-title:" + str(self.title) + "; farm:" + str(self.farm)
        if self.cad_number:
            return "cad-number:" + str(self.cad_number) + "; farm:" + str(self.farm)
        return "cad-id:" + str(self.id) + "; farm:" + str(self.farm)

    def get_pk_in_egistic_db(self):
        """
            If the cadastre does not exist in the egistic db, the method returns -1.
            Else returns primary key of the cadastre in the egistic db.
        """
        url = "{}{}".format(settings.EGISTIC_CADASTRE_QUERY_URL, self.cad_number)
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
            "Authorization": "Token {}".format(settings.EGISTIC_TOKEN),
        }

        r = requests.get(url, headers=headers)

        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        response_data = r.json()
        egistic_cadastre_pk = response_data["id"]

        return egistic_cadastre_pk

    def save(self, *args, **kwargs):
        if self.cad_number and not self.geom:
            url = "{}{}".format(settings.EGISTIC_CADASTRE_QUERY_URL, self.cad_number)
            headers = {
                "Content-type": "application/json",
                "Accept": "application/json",
                "Authorization": "Token {}".format(settings.EGISTIC_TOKEN),
            }

            r = requests.get(url, headers=headers)

            if r.status_code != requests.codes.ok:
                r.raise_for_status()
            response_data = r.json()
            self.geom = response_data["geomjson"]
        elif not self.cad_number and not self.geom:
            raise ValidationError("Either cad_number or geometry must be sent")
        elif self.cad_number and self.geom:
            raise ValidationError("Do not send cad_number and geometry together")

        super().save(*args, **kwargs)  # Call the "real" save() method.
