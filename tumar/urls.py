from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include, reverse_lazy
from django.views.generic.base import RedirectView

# from rest_auth.registration.views import (
#     SocialAccountListView,
#     SocialAccountDisconnectView,
# )
from rest_framework.routers import DefaultRouter

from .animals.views import (
    FarmViewSet,
    GeolocationAnimalViewSet,
    AnimalFarmViewSet,
    GetAnimalPathView,
    MachineryFarmViewSet,
    CadastreFarmViewSet,
    MyFarmView,
    SearchCadastreView,
    SimpleGroupedGeolocationsView,
    BreedingStockFarmViewSet,
    BreedingBullFarmViewSet,
    CalfFarmViewSet,
    StoreCattleFarmViewSet,
)
from .users.views import (
    UserViewSet,
    UserCreateViewSet,
    CustomAuthToken,
    NewAccountActivationView,
    SendSMSView,
    ResetPasswordView,
    ChangePhoneNumberView,
    CheckCodeView,
    # FacebookLogin,
    # GoogleLogin,
    # SocialAccountExtraView,
)
from .indicators.views import LatestIndicatorsView, RequestIndicatorsView
from .ecalendar.views import (
    CalfEventViewSet,
    BreedingStockEventViewSet,
    NextYearBreedingStockEventView,
    AllBreedingStockEventView,
    AllCalfEventView,
    CalendarView,
    ToggleBreedingStockEventView,
    ToggleCalfEventView,
)
from .catalog.views import CompanyDirectionListView, CompanyViewSet
from .community.views import (
    PostCategoryListView,
    PostReadOnlyViewSet,
    PostCreateView,
    PostUpdateDestroyView,
    PostImageDestroyView,
    PostVoteView,
    CommentListView,
    CommentCreateView,
    CommentUpdateDestroyView,
    CommentImageDestroyView,
    CommentVoteView,
    MyPostsView,
)
from .dashboard.views import (
    AnimalCountByTypeView,
    CalfToCowsRatioView,
    PastureToAnimalRatioView,
    BirthWeightAverageView,
    Predicted205DayWeightAverageView,
    CowEffectivenessAverageView,
    CowSKTAverageView,
    CowCountByYearView,
)
from .notify.views import NotificationListView

router = DefaultRouter()

router.register(r"users", UserViewSet)
router.register(r"users", UserCreateViewSet)
router.register(r"farms", FarmViewSet)
router.register(r"animals", AnimalFarmViewSet, basename="Animal")
router.register(r"breedingstock", BreedingStockFarmViewSet, basename="BreedingStock")
router.register(r"calf", CalfFarmViewSet, basename="Calf")
router.register(r"breedingbull", BreedingBullFarmViewSet, basename="BreedingBull")
router.register(r"storecattle", StoreCattleFarmViewSet, basename="StoreCattle")
router.register(r"geolocations", GeolocationAnimalViewSet)
router.register(r"machinery", MachineryFarmViewSet)
router.register(r"events/calf", CalfEventViewSet, basename="CalfEvent")
router.register(
    r"events/breedingstock", BreedingStockEventViewSet, basename="BreedingStockEvent"
)
router.register(r"cadastres", CadastreFarmViewSet, basename="Cadastre")
router.register(r"catalog", CompanyViewSet, basename="Catalog")
router.register(r"community/posts", PostReadOnlyViewSet, basename="Community")

urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    # Custom API endpoints
    path(
        "api/v1/",
        include(
            [
                path("users/activate-account/", NewAccountActivationView.as_view()),
                path("users/send-sms/", SendSMSView.as_view()),
                path("users/check-code/", CheckCodeView.as_view()),
                path("users/reset-password/", ResetPasswordView.as_view()),
                path("users/change-phone-num/", ChangePhoneNumberView.as_view()),
                path("get-path/", GetAnimalPathView.as_view(), name="get_path"),
                path(
                    "latest-geolocs/",
                    SimpleGroupedGeolocationsView.as_view(),
                    name="latest_grouped_geolocations",
                ),
                # path(
                #     "users/social-account-has-phone-number/",
                #     SocialAccountExtraView.as_view(),
                # ),
                path("cadastres/search-cadastre/", SearchCadastreView.as_view()),
                path("myfarm/", MyFarmView.as_view()),
                path("indicators/latest/", LatestIndicatorsView.as_view()),
                path("indicators/request/", RequestIndicatorsView.as_view()),
                path(
                    "events/breedingstock/<int:event_pk>/toggle/<uuid:animal_pk>/",
                    ToggleBreedingStockEventView.as_view(),
                ),
                path(
                    "events/calf/<int:event_pk>/toggle/<uuid:animal_pk>/",
                    ToggleCalfEventView.as_view(),
                ),
                path(
                    "events/breedingstock/next-year/",
                    NextYearBreedingStockEventView.as_view(),
                ),
                path(
                    "breedingstock/<uuid:pk>/events/",
                    AllBreedingStockEventView.as_view(),
                ),
                path("calf/<uuid:pk>/events/", AllCalfEventView.as_view()),
                path("events/calendar/<uuid:pk>/", CalendarView.as_view()),
                path("catalog/directions/", CompanyDirectionListView.as_view()),
                path("community/categories/", PostCategoryListView.as_view()),
                path("community/posts/create/", PostCreateView.as_view()),
                path("community/posts/my/", MyPostsView.as_view()),
                path("community/posts/<int:post_pk>/", PostUpdateDestroyView.as_view()),
                path(
                    "community/post-image/<int:img_pk>/",
                    PostImageDestroyView.as_view(),
                ),
                path(
                    "community/posts/<int:post_pk>/vote/<str:vote_type>/",
                    PostVoteView.as_view(),
                ),
                path(
                    "community/posts/<int:post_pk>/comments/",
                    CommentListView.as_view(),
                ),
                path("community/comments/", CommentCreateView.as_view(),),
                path(
                    "community/comments/<int:comment_pk>/",
                    CommentUpdateDestroyView.as_view(),
                ),
                path(
                    "community/comment-image/<int:img_pk>/",
                    CommentImageDestroyView.as_view(),
                ),
                path(
                    "community/comments/<int:comment_pk>/vote/<str:vote_type>/",
                    CommentVoteView.as_view(),
                ),
                path(
                    "dashboard/animal-count-by-type/", AnimalCountByTypeView.as_view()
                ),
                path("dashboard/calf-to-cows-ratio/", CalfToCowsRatioView.as_view()),
                path(
                    "dashboard/pasture-to-animal-ratio-view/",
                    PastureToAnimalRatioView.as_view(),
                ),
                path(
                    "dashboard/birth-weight-average/", BirthWeightAverageView.as_view()
                ),
                path(
                    "dashboard/predicted-205-day-weight-average/",
                    Predicted205DayWeightAverageView.as_view(),
                ),
                path(
                    "dashboard/cow-effectiveness-average/",
                    CowEffectivenessAverageView.as_view(),
                ),
                path("dashboard/cow-skt-average/", CowSKTAverageView.as_view()),
                path("dashboard/cow-count-by-year/", CowCountByYearView.as_view()),
                path("notifications/latest/", NotificationListView.as_view()),
            ]
            + router.urls
        ),
    ),
    path("api-token-auth/", CustomAuthToken.as_view()),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # django-rest-auth
    path("rest-auth/", include("rest_auth.urls")),
    # path("rest-auth/facebook/", FacebookLogin.as_view(), name="fb_login"),
    # path("rest-auth/google/", GoogleLogin.as_view(), name="ggl_login"),
    # path("accounts/", include("allauth.urls"), name="socialaccount_signup"),
    # path(
    #     "socialaccounts/", SocialAccountListView.as_view(), name="social_account_list"
    # ),
    # path(
    #     "socialaccounts/<int:pk>/disconnect/",
    #     SocialAccountDisconnectView.as_view(),
    #     name="social_account_disconnect",
    # ),
    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
    # If no prefix is given, use the default language
    prefix_default_language=False,
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
