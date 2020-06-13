from django.conf import settings
from django.db import models

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

    def mark_as_read(self):
        self.read = True
        self.save()

    def send(self):
        self.receiver.device_set.send_message(self.content)
