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
