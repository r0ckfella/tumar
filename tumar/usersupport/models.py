import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Create your models here.


class SupportTicket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="support_tickets",
        verbose_name=_("User"),
    )
    content = models.CharField(max_length=255, verbose_name=_("Content"))
    response = models.CharField(max_length=255, blank=True, verbose_name=_("Response"))
    answered = models.BooleanField(default=False, verbose_name=_("Answered?"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    answered_at = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Answered At"),
    )

    def mark_as_answered(self):
        self.answered = True
        self.answered_at = datetime.datetime.now()
        self.save()

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        if not is_new and not SupportTicket.objects.get(pk=self.pk).response:
            self.mark_as_answered()

        super().save(*args, **kwargs)
