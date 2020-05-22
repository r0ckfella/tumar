import uuid
import requests

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import gettext_lazy as _

from rest_framework.authtoken.models import Token
from faker import Factory as FakerFactory

from .utils import compress

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

    def save(self, *args, **kwargs):
        if self.image:
            # call the compress function
            new_image = compress(self.image)

            # set self.image to new_image
            self.image = new_image

        super().save(*args, **kwargs)


NEW_ACCOUNT = "NA"
RESET_PASSWORD = "RP"
NEW_PHONE_NUM = "NP"
OLD_PHONE_NUM = "OP"

SMS_TYPE_CHOICES = [
    (NEW_ACCOUNT, _("New Account Activation")),
    (RESET_PASSWORD, _("Reset Password")),
    (NEW_PHONE_NUM, _("New Phone Number")),
    (OLD_PHONE_NUM, _("Old Phone Number")),
]


class SMSVerification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sms_codes",
        null=True,
    )
    code = models.CharField(max_length=6, blank=True)
    activated = models.BooleanField(default=False)
    type = models.CharField(
        max_length=2,
        choices=SMS_TYPE_CHOICES,
        default=NEW_ACCOUNT,
        verbose_name=_("Type of the SMS Verification"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    phone_num = models.CharField(
        _("Phone Number"),
        max_length=16,
        null=True,
        help_text=_(
            "Required. Phone number must be entered in the format: '+77076143537'. "
            "Up to 15 digits allowed."
        ),
        validators=[main_validator],
    )

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            faker = FakerFactory.create()
            self.code = faker.numerify(text="######")

        super().save(*args, **kwargs)

    def activate_user(self, prompt_code: str):
        if self.code != prompt_code:
            return False

        self.user.is_active = True
        self.user.save()

        self.activate()
        return True

    def activate(self):
        self.activated = True
        self.save()

    def check_code(self, prompt_code: str):
        if self.code != prompt_code:
            return False
        return True

    def send_sms(self):
        temp_phone_num = None

        if self.user is None:
            temp_phone_num = self.phone_num
        else:
            temp_phone_num = self.user.username

        url = "https://smsc.kz/sys/send.php"
        payload = {
            "login": "waviot.asia",
            "psw": "moderator1",
            "phones": temp_phone_num,
            "mes": "Ваш проверочный код: {}".format(self.code),
        }

        r = requests.get(url, params=payload)

        if r.status_code != requests.codes.ok:
            print(r.text)
            r.raise_for_status()
            return False

        return True


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
