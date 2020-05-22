import logging

from rest_framework import viewsets, mixins, status
from rest_framework.authtoken.models import Token

from rest_framework.authtoken.views import ObtainAuthToken

from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny  # , IsAuthenticated
from rest_framework.response import Response

from rest_framework.views import APIView


from .models import User, NEW_ACCOUNT, SMSVerification, NEW_PHONE_NUM, OLD_PHONE_NUM
from .permissions import IsUserOrReadOnly

from .serializers import CreateUserSerializer, UserSerializer

logger = logging.getLogger(__name__)


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
                "image": request.build_absolute_uri(user.image.url)
                if user.image
                else None,
            }
        )


class NewAccountActivationView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        JSON fields:
        - phone_num: str
        - code: str
        """
        user = get_object_or_404(User, username=request.data["phone_num"])
        verification = SMSVerification.objects.filter(
            user=user, activated=False, type=NEW_ACCOUNT
        ).latest("created_at")
        is_activated = verification.activate_user(request.data["code"])

        if not is_activated:
            return Response(
                {"activated?": is_activated}, status=status.HTTP_404_NOT_FOUND
            )

        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"activated?": is_activated, "token": token.key}, status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        JSON fields:
        - key: str
        - new_password: str
        """
        verification = get_object_or_404(SMSVerification, pk=request.data["key"])
        if verification.activated:
            return Response(
                {"fail": "This code was already used."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user = verification.user
        user.set_password(request.data["new_password"])
        user.save()
        verification.activate()
        return Response({"success": True}, status=status.HTTP_200_OK)


class ChangePhoneNumberView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        JSON fields:
        - old_phone_num_key: str
        - new_phone_num_key: str
        - new_phone_num: str
        """
        user = get_object_or_404(
            SMSVerification, pk=request.data["old_phone_num_key"], type=OLD_PHONE_NUM
        ).user

        if not SMSVerification.objects.filter(
            pk=request.data["new_phone_num_key"], type=NEW_PHONE_NUM
        ).exists():
            return Response(
                {"fail": "Security error"}, status=status.HTTP_403_FORBIDDEN
            )

        user.username = request.data["new_phone_num"]
        user.save()

        return Response({"success": True}, status=status.HTTP_200_OK)


class CheckCodeView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        JSON fields:
        - phone_num: str
        - type: str
        - code: str
        Returns
        - key: uuid str
        """
        verification = None
        try:
            user = User.objects.get(username=request.data["phone_num"])
            verification = SMSVerification.objects.filter(
                user=user, activated=False, type=request.data["type"],
            ).latest("created_at")
        except User.DoesNotExist:
            verification = SMSVerification.objects.filter(
                phone_num=request.data["phone_num"],
                activated=False,
                type=request.data["type"],
            ).latest("created_at")
        except SMSVerification.DoesNotExist:
            logger.error("SMSVerification.DoesNotExist: {}".format(request.data))

        is_same = verification.check_code(request.data["code"])

        if not is_same:
            return Response({"fail": "wrong code"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"key": verification.pk}, status=status.HTTP_200_OK)


class SendSMSView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        JSON fields:
        - phone_num: str
        - type: str
        """
        verification = None
        verification = None
        try:
            user = User.objects.get(username=request.data["phone_num"])
            user.sms_codes.filter(type=request.data["type"]).update(
                activated=True
            )  # questionable
            verification = user.sms_codes.create(type=request.data["type"])
        except User.DoesNotExist:
            verification = SMSVerification.objects.create(
                type=NEW_PHONE_NUM, phone_num=request.data["phone_num"]
            )

        # Sending the SMS
        if not verification.send_sms():
            verification.delete()
            return Response({"sent?": False}, status=status.HTTP_404_NOT_FOUND)

        return Response({"sent?": True}, status=status.HTTP_200_OK)
