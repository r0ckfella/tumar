import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tumar.animals.models import Cadastre, Farm

# Create your models here.

PENDING = 'PE'
FAILURE = 'FA'
FINISHED = 'FI'

STATUS_CHOICES = [
    (PENDING, _('Pending')),
    (FAILURE, _('Failure')),
    (FINISHED, _('Finished')),
]

class ImageryRequest(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE,
                             related_name="imagery_requests", verbose_name=_('Farm'))
    cadastre = models.ForeignKey(Cadastre, on_delete=models.CASCADE,
                                 related_name="imagery_requests", verbose_name=_('Cadastre'))
    generate_bands = models.BooleanField(default=False)
    process_status = models.CharField(max_length=2, choices=STATUS_CHOICES,
                                      default=PENDING, verbose_name=_('Current request status'))
    created_date = models.DateTimeField(default=timezone.now, verbose_name=_('Entry Creation Date'))
    requested_date = models.DateField(verbose_name=_('Requested date'))
    actual_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Actual Date'))
    results_dir = models.CharField(max_length=100, blank=True, verbose_name=_('Directory with results'))

    def save(self, *args, **kwargs):
        # !!! requested_date is timezone.now()
        self.requested_date = datetime.date.today()
        super(ImageryRequest, self).save(*args, **kwargs)
        from .tasks import main_request_fetch
        main_request_fetch(imagery_request=self, requested_date=self.requested_date,
                           generate_bands=self.generate_bands)

    def success(self, results_dir, image_date, *args, **kwargs):
        if self.process_status == PENDING:
            self.actual_date = image_date
            self.results_dir = results_dir
            self.process_status = FINISHED
            self.save()
        print("ImageryRequest's success() method shouldn't have been called with any process_status other than PENDING")
        self.failure()

    def failure(self, *args, **kwargs):
        self.process_status = FAILURE
        self.save()
