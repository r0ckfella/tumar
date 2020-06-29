from django.conf import settings
from django.db import models

from .managers import NotificationManager

# Create your models here.


class Notification(models.Model):
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    content = models.CharField(max_length=255, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    objects = NotificationManager()

    def mark_as_read(self):
        self.read = True
        self.save()

    def send(self, *args, **kwargs):
        if settings.PUSH_NOTIFICATIONS_SETTINGS.get("FCM_API_KEY", None):
            self.receiver.gcmdevice_set.all().send_message(
                self.content, *args, **kwargs
            )
