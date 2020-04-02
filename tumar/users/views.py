from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from django.utils.translation import gettext_lazy as _
from phone_verify.base import response
from phone_verify.services import send_security_code_and_generate_session_token
from phone_verify.api import VerificationViewSet
from phone_verify import serializers as phone_serializers
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_auth.registration.views import SocialLoginView
from rest_framework.views import APIView

from .models import User
from .permissions import IsUserOrReadOnly
from .services import create_user_account
from .serializers import (
    CreateUserSerializer,
    UserSerializer,
    SMSCreateUserSerializer,
    SMSPasswordResetSerializer,
    SMSPhoneNumberChangeSerializer,
)


class UserViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """
    Updates and retrieves user accounts
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


class UserCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Creates user accounts
    """

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class SocialAccountExtraView(APIView):
    """
    Retrieve
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        social_accounts = SocialAccount.objects.filter(
            user=request.user, socialaccount_extra__has_phone_number=True
        )

        if not social_accounts:
            raise NotFound(
                detail="No associated social accounts with this Tumar account"
            )

        return Response({"has_phone_number": True})


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "full_name": user.get_full_name(),
                "email": user.email,
                "phone_num": user.username,
            }
        )


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class CustomVerificationViewSet(VerificationViewSet):
    def register(self, request):
        pass

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=phone_serializers.PhoneSerializer,
    )
    def send_sms(self, request):
        serializer = phone_serializers.PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_token = send_security_code_and_generate_session_token(
            str(serializer.validated_data["phone_number"])
        )
        return response.Ok({"session_token": session_token})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=SMSCreateUserSerializer,
    )
    def verify_and_register(self, request):
        """
        Function to verify phone number and register a user
        """

        serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer = SMSCreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("password2")
        serializer.validated_data.pop("session_token")
        serializer.validated_data.pop("security_code")
        user = create_user_account(**serializer.validated_data)

        return Response(
            {"detail": _("User {} was successfully created.").format(user.username)}
        )

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[AllowAny],
        serializer_class=SMSPasswordResetSerializer,
    )
    def verify_and_reset_password(self, request):
        """
        Function to verify phone number and reset the password
        """

        serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer = SMSPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": _("Password has been reset with the new password.")})

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=[IsAuthenticated],
        serializer_class=SMSPhoneNumberChangeSerializer,
    )
    def verify_and_change_phone_number(self, request):
        """
        Function to verify phone number and change the phone number to another one
        """
        serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(User, username=request.user)

        # Borodatyi code
        serializer = SMSPhoneNumberChangeSerializer(
            user,
            data={"new_phone_number": request.data.get("new_phone_number")},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": _("New phone number has been saved.")})
