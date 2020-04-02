from allauth.account.adapter import DefaultAccountAdapter
from allauth.account import app_settings
from django.core.exceptions import ValidationError
from faker import Factory as FakerFactory

from .models import main_validator, User

faker = FakerFactory.create()


def generate_phone_number():
    invalid = True
    exists = True  # assuming a generated phone number exists
    phone_number = None

    while invalid or exists:
        phone_number = faker.numerify(text="###########")
        try:
            main_validator(phone_number)
        except ValidationError:
            invalid = True
        else:
            invalid = False
            exists = User.objects.filter(username=phone_number).exists()

    return phone_number


class MyAccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        Fills in a valid username, if required and missing.  If the
        username is already present it is assumed to be valid
        (unique).
        """
        from allauth.account.utils import user_username, user_email, user_field

        first_name = user_field(user, "first_name")  # noqa
        last_name = user_field(user, "last_name")  # noqa
        email = user_email(user)  # noqa
        username = user_username(user)
        if app_settings.USER_MODEL_USERNAME_FIELD:
            user_username(user, username or generate_phone_number())
