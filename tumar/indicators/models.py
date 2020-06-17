import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import connections, models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tumar.animals.models import Cadastre

from .choices import STATUS_CHOICES, PENDING, FREE_EXPIRED, FAILED, PROCESSING, WAITING
from .exceptions import (
    QueryImageryFromEgisticError,
    FreeRequestsExpiredError,
    CadastreNotInEgisticError,
    ImageryRequestAlreadyExistsError,
)

logger = logging.getLogger(__name__)

# Create your models here.


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

    def start_image_processing(self, disable_check=False, immediate=True):
        if not disable_check and not self.cadastre.farm.has_free_request():
            self.status = FREE_EXPIRED
            self.save()
            raise FreeRequestsExpiredError(farm_pk=self.cadastre.farm.pk)

        egistic_cadastre_pk = self.cadastre.get_pk_in_egistic_db()
        if egistic_cadastre_pk == -1:
            self.status = FAILED
            self.save()
            raise CadastreNotInEgisticError(cadastre_pk=self.cadastre.pk)

        if not immediate:
            self.status = WAITING
        else:
            self.status = PROCESSING

        self.save()

        from .tasks import run_image_processing_task

        run_image_processing_task(self, egistic_cadastre_pk, immediate)

    def has_enough_time_diff(self):
        if ImageryRequest.objects.filter(
            cadastre=self.cadastre,
            requested_date__gt=self.requested_date
            - timedelta(days=settings.DAYS_BETWEEN_IMAGERY_REQUESTS),
        ).exists():
            return False

        return True

    def save_result_after_success(self, imagination_result):
        # Save imagery data into the db
        self.ndvi = imagination_result["imagery_request"]["ndvi"]
        self.gndvi = imagination_result["imagery_request"]["gndvi"]
        self.clgreen = imagination_result["imagery_request"]["clgreen"]
        self.ndmi = imagination_result["imagery_request"]["ndmi"]
        self.ndsi = imagination_result["imagery_request"]["ndsi"]
        self.finished_at = imagination_result["imagery_request"]["actual_date"]
        self.results_dir = imagination_result["imagery_request"]["results_dir"]
        self.is_layer_created = imagination_result["imagery_request"][
            "is_layer_created"
        ]
        self.save()

        # Save PNGs into the db
        self.ndvi_dir = imagination_result["ir_pngs"]["ndvi"]
        self.gndvi_dir = imagination_result["ir_pngs"]["gndvi"]
        self.clgreen_dir = imagination_result["ir_pngs"]["clgreen"]
        self.ndmi_dir = imagination_result["ir_pngs"]["ndmi"]
        self.rgb_dir = imagination_result["ir_pngs"]["rgb"]
        self.save()

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if not self.requested_date:
            self.requested_date = timezone.now().date()

        if (
            is_new
            and ImageryRequest.objects.filter(
                cadastre=self.cadastre, requested_date=self.requested_date
            )
            .exclude(Q(status__exact=FAILED) | Q(status__exact=FREE_EXPIRED))
            .exists()
        ):
            raise ImageryRequestAlreadyExistsError(cadastre_pk=self.cadastre.pk)

        super().save(*args, **kwargs)
