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

    def send(self, extra=None, *args, **kwargs):
        if settings.PUSH_NOTIFICATIONS_SETTINGS.get("FCM_API_KEY", None):
            if extra:
                extra.update(
                    {
                        "collapse_key": "com.development.tumar_app",
                        "google.original_priority": "high",
                        "google.delivered_priority": "high",
                        "click_action": "FLUTTER_NOTIFICATION_CLICK",
                    }
                )
            self.receiver.gcmdevice_set.all().send_message(
                self.content, *args, **kwargs
            )
