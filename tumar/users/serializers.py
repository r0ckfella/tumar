import requests
import json

from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from .models import User, SMSVerification


class UserPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "image",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "image",
        )
        read_only_fields = ("username",)


class CreateUserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    def create(self, validated_data):
        # call create_user on user object. Without this
        # the password will be stored in plain text.
        user = User.objects.create_user(**validated_data, active=False)

        # Creating verification SMS code and saving to DB
        verification = SMSVerification.objects.create(user=user)

        # Sending the SMS
        url = "https://smsc.kz/sys/send.php"
        payload = {
            "login": "waviot.asia",
            "psw": "moderator1",
            "phones": user.username,
            "mes": "Ваш код: {}".format(verification.code),
            "sender": "Tumar",
        }

        r = requests.get(url, params=payload)

        if r.status_code != requests.codes.ok:
            print(r.text)
            r.raise_for_status()

        return user

    def get_token(self, user):
        token, created = Token.objects.get_or_create(user=user)
        return token.key

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "token",
        )
        read_only_fields = ("token",)
        extra_kwargs = {"password": {"write_only": True}}


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        self.logout_on_password_change = getattr(
            settings, "LOGOUT_ON_PASSWORD_CHANGE", False
        )
        super(PasswordResetSerializer, self).__init__(*args, **kwargs)

        self._errors = {}
        self.user = None
        self.set_password_form = None

    def validate(self, attrs):

        try:
            self.user = User.objects.get(username=attrs["phone_number"])
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({"id": ["Invalid value"]})

        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)

        return attrs

    def save(self):
        return self.set_password_form.save()


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, required=True)
    new_password1 = serializers.CharField(max_length=128, required=True)
    new_password2 = serializers.CharField(max_length=128, required=True)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = getattr(
            settings, "OLD_PASSWORD_FIELD_ENABLED", False
        )
        self.logout_on_password_change = getattr(
            settings, "LOGOUT_ON_PASSWORD_CHANGE", False
        )
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop("old_password")

        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)
        self.set_password_form = None

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError("Invalid password")
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(self.request, self.user)


class SMSPhoneNumberChangeSerializer(serializers.ModelSerializer):
    """
    Serializer for changing phone number.
    """

    new_phone_number = serializers.CharField(source="username", required=True)
    # phone_number = PhoneNumberField(required=True)
    session_token = serializers.CharField(required=True)
    security_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "new_phone_number",
            "phone_number",
            "session_token",
            "security_code",
        )
        extra_kwargs = {
            "new_phone_number": {"write_only": True},
            "phone_number": {"write_only": True},
            "session_token": {"write_only": True},
            "security_code": {"write_only": True},
        }
