import logging
import traceback

from datetime import timedelta

from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.db import models, connections
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tumar.animals.models import Cadastre
from ..celery import app

logger = logging.getLogger(__name__)

# Create your models here.

PENDING = "PE"
WAITING = "WA"
PROCESSING = "PR"
SUCCESS = "SU"
FAILURE = "FA"
FREE_EXPIRED = "FE"

STATUS_CHOICES = [
    (PENDING, _("Pending")),
    (WAITING, _("Waiting for new imagery")),
    (PROCESSING, _("Processing")),
    (SUCCESS, _("Success")),
    (FAILURE, _("Failure")),
    (FREE_EXPIRED, _("Free requests expired")),
]


class ImageryRequest(models.Model):
    cadastre = models.ForeignKey(
        Cadastre,
        on_delete=models.CASCADE,
        related_name="imagery_requests",
        verbose_name=_("Cadastre"),
    )
    ndvi = JSONField(blank=True, null=True)
    gndvi = JSONField(blank=True, null=True)
    clgreen = JSONField(blank=True, null=True)
    ndmi = JSONField(blank=True, null=True)
    ndsi = JSONField(blank=True, null=True)
    created_at = models.DateField(
        auto_now_add=True, verbose_name=_("Request creation date")
    )
    requested_date = models.DateField(
        default=timezone.now, verbose_name=_("Request scheduled time")
    )
    finished_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Request finish time")
    )
    results_dir = models.TextField(blank=True, null=True)
    is_layer_created = models.BooleanField(blank=True, null=True)
    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default=PENDING, verbose_name=_("Status"),
    )

    class Meta:
        verbose_name = _("Imagery Request")
        verbose_name_plural = _("Imagery Requests")

    def start_task(self, disable_check=False):
        if not disable_check and self.cadastre.farm.has_free_request():
            logger.warning(
                "{} farm's free requests have expired.".format(self.cadastre.farm)
            )
            self.status = FREE_EXPIRED
            self.save()
            return False

        if not self.has_available_imagery():
            logger.warning(
                "The cadastre {} has been put into the queue for imagery.".format(
                    self.cadastre
                )
            )
            self.status = WAITING
            self.save()
            return False

        egistic_cadastre_id = None

        try:
            with connections["egistic_2"].cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM cadastres_cadastre WHERE kad_nomer = %s",
                    [self.cadastre.cad_number],
                )
                row = cursor.fetchone()
                egistic_cadastre_id = row[0]
        except Exception as e:  # noqa
            logger.error(traceback.format_exc())
            logger.error(
                "Cadastre number {} was not found in the egistic db."
                + "Or imagery for custom cadastres is not supported yet.".format(
                    self.cadastre.cad_number
                )
            )
            self.status = FAILURE
            self.save()
            return False

        target_dates = [
            self.requested_date,
        ]

        self.status = PROCESSING
        self.save()

        # TODO move this to a django-celery task that monitors status and changes it.
        # SUCCESS and FAILURE are set here. When Success or Failure, it sends
        # a notification to a new notification queue which is triggered when the user
        # logs in
        result = app.signature(
            "process_cadastres",
            kwargs={
                "param_values": dict(param="id", values=[egistic_cadastre_id]),
                "target_dates": target_dates,
                "days_range": 14,
            },
            queue="process_cadastres",
            priority=5,
        )
        result.delay()

        return True

    def has_available_imagery(self):
        # TODO alter imagination for this functionality
        # a simple check if there is enough imagery products to provide the indicators
        pass

    def has_enough_time_diff(self):
        if ImageryRequest.objects.filter(
            cadastre=self.cadastre,
            requested_date__gt=self.requested_date
            - timedelta(days=settings.DAYS_BETWEEN_IMAGERY_REQUESTS),
        ).exists():
            return False

        return True

    def save(self, *args, **kwargs):
        if (
            ImageryRequest.objects.filter(
                cadastre=self.cadastre, requested_date=self.requested_date
            )
            .exclude(Q(status__exact=FAILURE) | Q(status__exact=FREE_EXPIRED))
            .exists()
        ):
            logger.info(
                "The cadastre {} is already in the queue for image processing.".format(
                    self.cadastre
                )
            )
            return

        super().save(*args, **kwargs)
        self.start_task()
