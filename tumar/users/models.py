import uuid

# from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

main_validator = RegexValidator(
    regex=r"^\+\d{11}$",
    message=(
        "Phone number must be entered in the format: '+77076143537' or '77076143537'. "
        "Up to 15 digits allowed."
    ),
)


@python_2_unicode_compatible
class User(AbstractUser):
    username_validator = main_validator

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        _("Phone Number"),
        max_length=16,
        unique=True,
        null=True,
        help_text=_(
            "Required. Phone number must be entered in the format: '+77076143537'. "
            "Up to 15 digits allowed."
        ),
        validators=[username_validator],
        error_messages={"unique": _("A user with that phone number already exists.")},
    )
    image = models.ImageField(
        upload_to="userimages",
        max_length=150,
        null=True,
        blank=True,
        verbose_name=_("Profile Picture"),
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.username


# class SocialAccountExtra(models.Model):
#     socialaccount = models.OneToOneField(
#         SocialAccount,
#         on_delete=models.CASCADE,
#         primary_key=True,
#         related_name="socialaccount_extra",
#         verbose_name=_("Social Account"),
#     )
#     has_phone_number = models.BooleanField(
#         default=False, verbose_name=_("Has Phone Number?")
#     )

#     class Meta:
#         verbose_name = _("Social Account Extra")
#         verbose_name_plural = _("Social Accounts Extra")

#     def __str__(self):
#         return self.socialaccount.provider + self.socialaccount.user.email


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# @receiver(post_save, sender=SocialAccount)  # noqa
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         SocialAccountExtra.objects.create(socialaccount=instance)
