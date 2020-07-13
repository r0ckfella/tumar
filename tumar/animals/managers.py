import datetime

from dateutil.relativedelta import relativedelta

from django.contrib.gis.db.models.functions import Cast
from django.db import models
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
)
from django.db.models.functions import ExtractDay, Coalesce

from ..ecalendar.models import SingleCalfEvent, SingleBreedingStockEvent
from .choices import MALE, FEMALE


class GeolocationQuerySet(models.QuerySet):
    def get_path(self, animal_imei, start_time, end_time):
        return self.filter(
            animal__imei=animal_imei, time__range=(start_time, end_time)
        ).order_by("time")


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
