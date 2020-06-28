from django.db import models


class PostLinkManager(models.Manager):
    def youtube_links_count(self):
        return self.get_queryset().filter(type="Y").count()

    def general_links_count(self):
        return self.get_queryset().filter(type="G").count()
