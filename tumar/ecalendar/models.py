from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import DateRangeField

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
    # scheduled_date = models.DateField(
    #     default=datetime.date.today, verbose_name=_("Scheduled date of the event")
    # )
    scheduled_date_range = DateRangeField(
        verbose_name=_("Scheduled date range of the event")
    )
    completion_date = models.DateField(
        null=True, verbose_name=_("Date of the event completion")
    )
    type = models.CharField(
        max_length=2,
        choices=TYPE_CHOICES,
        default=OTHER,
        verbose_name=_("Type of the event"),
    )
    report = models.TextField(blank=True, verbose_name=_("Report"))
    completed = models.BooleanField(default=False, verbose_name=_("Completed?"))

    class Meta:
        abstract = True


class BreedingStockEvent(Event):
    animal = models.ForeignKey(
        BreedingStock,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name=_("Cow Animal of the event"),
    )

    class Meta:
        verbose_name = _("Cow Event")
        verbose_name_plural = _("Cow Events")

    def __str__(self):
        return str(self.animal) + ":" + str(self.title)


class CalfEvent(Event):
    animal = models.ForeignKey(
        Calf,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name=_("Calf Animal of the event"),
    )

    class Meta:
        verbose_name = _("Calf Event")
        verbose_name_plural = _("Calf Events")

    def __str__(self):
        return str(self.animal) + ":" + str(self.title)
