import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import connections, models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tumar.animals.models import Cadastre

from ..celery import app
from .tasks import log_error
from .exceptions import (
    QueryImageryFromEgisticError,
    FreeRequestsExpiredError,
    CadastreNotInEgisticError,
    ImageryRequestAlreadyExistsError,
)

logger = logging.getLogger(__name__)

# Create your models here.

PENDING = "PE"
WAITING = "WA"
PROCESSING = "PR"
FINISHED = "FI"
FAILED = "FA"
FREE_EXPIRED = "FE"

STATUS_CHOICES = [
    (PENDING, _("Pending")),
    (WAITING, _("Waiting for new imagery")),
    (PROCESSING, _("Processing")),
    (FINISHED, _("Finished")),
    (FAILED, _("Failed")),
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
    results_dir = models.CharField(max_length=120, blank=True, null=True)
    ndvi_dir = models.CharField(max_length=120, blank=True, null=True)
    gndvi_dir = models.CharField(max_length=120, blank=True, null=True)
    clgreen_dir = models.CharField(max_length=120, blank=True, null=True)
    ndmi_dir = models.CharField(max_length=120, blank=True, null=True)
    rgb_dir = models.CharField(max_length=120, blank=True, null=True)
    is_layer_created = models.BooleanField(blank=True, null=True)
    status = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default=PENDING, verbose_name=_("Status"),
    )

    class Meta:
        verbose_name = _("Imagery Request")
        verbose_name_plural = _("Imagery Requests")

    def start_task(self, disable_check=False):
        if not disable_check and self.cadastre.farm.has_free_request():
            self.status = FREE_EXPIRED
            self.save()
            raise FreeRequestsExpiredError(farm_pk=self.cadastre.farm.pk)

        # if not self.has_available_imagery():
        #     logger.warning(
        #         "The cadastre {} has been put into the queue for imagery.".format(
        #             self.cadastre
        #         )
        #     )
        #     self.status = WAITING
        #     self.save()
        #     return False

        egistic_cadastre_pk = None

        egistic_cadastre_pk = self.cadastre.get_pk_in_egistic_db()
        if egistic_cadastre_pk == -1:
            self.status = FAILED
            self.save()
            raise CadastreNotInEgisticError(cadastre_pk=self.cadastre.pk)

        target_dates = [
            self.requested_date,
        ]

        self.status = PROCESSING
        self.save()

        result = app.signature(
            "process_cadastres",
            kwargs={
                "param_values": dict(param="id", values=[egistic_cadastre_pk]),
                "target_dates": target_dates,
                "days_range": 14,
            },
            queue="process_cadastres",
            priority=5,
        )

        # TODO a django-celery task that monitors status and changes it.
        # FINISHED, WAITING, FAILED are set here. When FINISHED, WAITING, FAILED, it
        # sends a notification to a new notification queue which is triggered when the
        # user logs in. When WAITING, increases requested time one day further.
        result_handler_task_name = "tumar_handler_process_cadastres"
        handler_task = app.signature(
            result_handler_task_name,
            kwargs={"imageryrequest_id": self.id},
            queue=result_handler_task_name,
        )

        (result.on_error(log_error.s(imageryrequest_id=self.id)) | handler_task).delay()

        return True

    def has_enough_time_diff(self):
        if ImageryRequest.objects.filter(
            cadastre=self.cadastre,
            requested_date__gt=self.requested_date
            - timedelta(days=settings.DAYS_BETWEEN_IMAGERY_REQUESTS),
        ).exists():
            return False

        return True

    def fetch_result_after_success(self):
        egistic_cadastre_pk = self.cadastre.get_pk_in_egistic_db()
        if egistic_cadastre_pk == -1:
            self.status = FAILED
            self.save()
            raise CadastreNotInEgisticError(cadastre_pk=self.cadastre.pk)

        cadastre_result_pk = None

        # Fetch imagery data
        try:
            with connections["egistic_2"].cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM tumar_cadastreresult WHERE cadastre_id = %s ORDER BY"
                    + " actual_date DESC",
                    [egistic_cadastre_pk],
                )
                row = cursor.fetchone()
                cadastre_result_pk = row[0]
                self.ndvi = row[1]
                self.gndvi = row[2]
                self.clgreen = row[3]
                self.ndmi = row[4]
                self.ndsi = row[5]
                self.finished_at = row[6]
                self.results_dir = row[7]
                self.is_layer_created = row[9]
                self.save()
        except Exception:
            self.status = FAILED
            self.save()
            raise QueryImageryFromEgisticError(cadastre_pk=self.cadastre.pk)

        # Fetch PNGs
        try:
            with connections["egistic_2"].cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM tumar_cadastreresultimage WHERE"
                    + " cadastreresult_id = %s",
                    [cadastre_result_pk],
                )
                row = cursor.fetchone()
                self.ndvi_dir = row[1]
                self.gndvi_dir = row[2]
                self.clgreen_dir = row[3]
                self.ndmi_dir = row[4]
                self.rgb_dir = row[5]
                self.save()
        except Exception:
            self.status = FAILED
            self.save()
            raise QueryImageryFromEgisticError(cadastre_pk=self.cadastre.pk)

    def save(self, *args, **kwargs):
        if not self.requested_date:
            self.requested_date = timezone.now().date()
        if (
            self._state.adding is True
            and ImageryRequest.objects.filter(
                cadastre=self.cadastre, requested_date=self.requested_date
            )
            .exclude(Q(status__exact=FAILED) | Q(status__exact=FREE_EXPIRED))
            .exists()
        ):
            raise ImageryRequestAlreadyExistsError(cadastre_pk=self.cadastre.pk)

        super().save(*args, **kwargs)

        if self._state.adding is True:
            self.start_task()
