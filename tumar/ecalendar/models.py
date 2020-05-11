from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import DateRangeField, JSONField

from tumar.animals.models import BreedingStock, Calf

# Create your models here.


HANDLING = "HL"
HEALTH = "HT"
FEEDING = "FD"
OTHER = "OT"

TYPE_CHOICES = [
    (HANDLING, _("Управление")),
    (HEALTH, _("Здоровье")),
    (FEEDING, _("Кормление")),
    (OTHER, _("Остальное")),
]


class Event(models.Model):
    title = models.CharField(max_length=80, verbose_name=_("Title"))
    scheduled_date_range = DateRangeField(
        verbose_name=_("Scheduled date range of the event")
    )
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=OTHER,
        verbose_name=_("Type of the event"),
    )
    report = models.TextField(blank=True, verbose_name=_("Report"))
    attributes = JSONField(null=True, blank=True)

    class Meta:
        abstract = True


class BreedingStockEvent(Event):
    animals = models.ManyToManyField(
        BreedingStock,
        through="SingleBreedingStockEvent",
        related_name="events",
        verbose_name=_("Cow Animal of the event"),
    )

    class Meta:
        verbose_name = _("Cow Event")
        verbose_name_plural = _("Cow Events")

    def __str__(self):
        return str(self.title)


class SingleBreedingStockEvent(models.Model):
    event = models.ForeignKey(BreedingStockEvent, on_delete=models.CASCADE)
    animal = models.ForeignKey(BreedingStock, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False, verbose_name=_("Completed?"))
    completion_date = models.DateField(
        null=True, blank=True, verbose_name=_("Date of the event completion")
    )


class CalfEvent(Event):
    animals = models.ManyToManyField(
        Calf,
        through="SingleCalfEvent",
        related_name="events",
        verbose_name=_("Calf Animal of the event"),
    )

    class Meta:
        verbose_name = _("Calf Event")
        verbose_name_plural = _("Calf Events")

    def __str__(self):
        return str(self.title)


class SingleCalfEvent(models.Model):
    event = models.ForeignKey(CalfEvent, on_delete=models.CASCADE)
    animal = models.ForeignKey(Calf, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False, verbose_name=_("Completed?"))
    completion_date = models.DateField(
        null=True, blank=True, verbose_name=_("Date of the event completion")
    )
