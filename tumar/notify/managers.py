from django.db import models


class NotificationManager(models.Manager):
    def unread_count(self):
        return self.get_queryset().filter(read=False).count()
