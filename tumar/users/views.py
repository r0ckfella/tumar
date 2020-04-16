# from allauth.socialaccount.models import SocialAccount
# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
# from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, mixins
from rest_framework.authtoken.models import Token

from rest_framework.authtoken.views import ObtainAuthToken

# from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny  # , IsAuthenticated
from rest_framework.response import Response

# from rest_framework.views import APIView

# from rest_auth.registration.views import SocialLoginView

from .models import User
from .permissions import IsUserOrReadOnly

# from .services import create_user_account
from .serializers import (
    CreateUserSerializer,
    UserSerializer,
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


# class SocialAccountExtraView(APIView):
#     """
#     Retrieve
#     """

#     permission_classes = (IsAuthenticated,)

#     def get(self, request, format=None):
#         social_accounts = SocialAccount.objects.filter(
#             user=request.user, socialaccount_extra__has_phone_number=True
#         )

#         if not social_accounts:
#             raise NotFound(
#                 detail="No associated social accounts with this Tumar account"
#             )

#         return Response({"has_phone_number": True})


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


# class FacebookLogin(SocialLoginView):
#     adapter_class = FacebookOAuth2Adapter


# class GoogleLogin(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
