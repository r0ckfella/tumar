from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.

# [Лучшее, Новости, Животноводство, Ветеринария, Генетика, Растениеводство, Птицеводство, Сельхозтехника, Корма, Консультации, Общение, Барахолка, Обучение, Работа приложения]


class Category(models.Model):
    name = models.CharField(max_length=80, verbose_name=_("Name of the Category"))

    class Meta:
        verbose_name = _("Post Category")
        verbose_name_plural = _("Post Categories")

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name=_("Author"),
    )
    categories = models.ManyToManyField(
        Category, related_name="posts", verbose_name=_("Categories of the Post"),
    )
    title = models.CharField(max_length=100, verbose_name=_("Title of the Post"))
    content = models.TextField(verbose_name=_("Content of the Post"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # TODO VideoField optional

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")

    def __str__(self):
        return str(self.pk) + ": " + self.title


class PostImage(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="images", verbose_name=_("Post"),
    )
    image = models.ImageField(upload_to="postimages", max_length=150)

    class Meta:
        verbose_name = _("Post Image")
        verbose_name_plural = _("Post Images")


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comments",
        verbose_name=_("User"),
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments", verbose_name=_("Post"),
    )
    reply_object = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("Object of the Reply"),
    )
    content = models.TextField(verbose_name=_("Content of the Comment"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # TODO VideoField optional

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    def __str__(self):
        return str(self.pk) + ": " + self.title

    def delete(self, *args, **kwargs):

        if self.replies.all().exists():
            self.user = None
            self.content = "[удален]"
            self.save()
        else:
            super().delete(*args, **kwargs)  # Call the "real" delete() method.


class CommentImage(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Comment"),
    )
    image = models.ImageField(upload_to="commentimages", max_length=150)

    class Meta:
        verbose_name = _("Comment Image")
        verbose_name_plural = _("Comment Images")
