from django.utils.translation import gettext_lazy as _
from phone_verify.base import response
from phone_verify.services import send_security_code_and_generate_session_token
from phone_verify.api import VerificationViewSet
from phone_verify import serializers as phone_serializers
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView

from .models import User
from .permissions import IsUserOrReadOnly
from .services import create_user_account
from .serializers import CreateUserSerializer, UserSerializer, SMSCreateUserSerializer, SMSPasswordResetSerializer, \
    SMSPasswordChangeSerializer


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (IsAdminUser,)


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'full_name': user.get_full_name(),
            'email': user.email,
            'phone_num': user.phone_num
        })


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class CustomVerificationViewSet(VerificationViewSet):

    def register(self, request):
        pass

    @action(detail=False, methods=["POST"], permission_classes=[AllowAny],
            serializer_class=phone_serializers.PhoneSerializer)
    def send_sms(self, request):
        serializer = phone_serializers.PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_token = send_security_code_and_generate_session_token(
            str(serializer.validated_data["phone_number"])
        )
        return response.Ok({"session_token": session_token})

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny],
            serializer_class=SMSCreateUserSerializer)
    def verify_and_register(self, request):
        """Function to verify phone number and register a user

        Most of the code here is corresponding to the "verify" view already present in the package.

        """

        serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer = SMSCreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('password2')
        serializer.validated_data.pop('session_token')
        serializer.validated_data.pop('security_code')
        user = create_user_account(**serializer.validated_data)

        return Response(
            {"detail": _("User {} was successfully created.").format(user.username)}
        )

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny],
            serializer_class=SMSPasswordResetSerializer)
    def verify_and_reset_password(self, request):
        """Function to verify phone number and reset the password

        Most of the code here is corresponding to the "verify" view already present in the package.

        """

        serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer = SMSPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": _("Password has been reset with the new password.")}
        )

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated],
            serializer_class=SMSPasswordChangeSerializer)
    def verify_and_change_password(self, request):
        """Function to verify phone number and change the password

        Most of the code here is corresponding to the "verify" view already present in the package.

        """

        serializer = phone_serializers.SMSVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer = SMSPasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": _("New password has been saved.")})
