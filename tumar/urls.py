from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include, reverse_lazy
from django.views.generic.base import RedirectView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.routers import DefaultRouter
from push_notifications.api.rest_framework import GCMDeviceAuthorizedViewSet, APNSDeviceAuthorizedViewSet

from .animals.views import (
    FarmViewSet,
    GeolocationAnimalViewSet,
    AnimalViewSet,
    GetAnimalPathView,
    MachineryViewSet,
    CadastreViewSet,
    MyFarmView,
    SearchCadastreView,
    SimpleGroupedGeolocationsView,
    BreedingStockViewSet,
    BreedingBullViewSet,
    CalfViewSet,
    StoreCattleViewSet,
    ConvertToAdultView,
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
)
from .indicators.views import LatestIndicatorsView, RequestIndicatorsView
from .ecalendar.views import (
    CalfEventViewSet,
    BreedingStockEventViewSet,
    ToggleBreedingStockEventView,
    ToggleCalfEventView,
    BreedingStockMeasurementView,
    CalfMeasurementView,
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
from .notify.views import NotificationListView, NotificationMarkAsReadView
from .usersupport.views import SupportTicketCreateView

router = DefaultRouter()

router.register(r"users", UserViewSet)
router.register(r"users", UserCreateViewSet)
router.register(r"farms", FarmViewSet, basename="Farm")
router.register(r"animals", AnimalViewSet, basename="Animal")
router.register(r"breedingstock", BreedingStockViewSet, basename="BreedingStock")
router.register(r"calf", CalfViewSet, basename="Calf")
router.register(r"breedingbull", BreedingBullViewSet, basename="BreedingBull")
router.register(r"storecattle", StoreCattleViewSet, basename="StoreCattle")
router.register(r"geolocations", GeolocationAnimalViewSet, basename="Geolocation")
router.register(r"machinery", MachineryViewSet, basename="Machinery")
router.register(r"events/calf", CalfEventViewSet, basename="CalfEvent")
router.register(
    r"events/breedingstock", BreedingStockEventViewSet, basename="BreedingStockEvent"
)
router.register(r"cadastres", CadastreViewSet, basename="Cadastre")
router.register(r"catalog", CompanyViewSet, basename="Catalog")
router.register(r"community/posts", PostReadOnlyViewSet, basename="Community")
router.register(r"device/gcm", GCMDeviceAuthorizedViewSet)
router.register(r"device/apns", APNSDeviceAuthorizedViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Tumar Web API",
        default_version="v1",
        description="Web API for Tumar Mobile Application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="epmek96@gmail.com"),
        license=openapi.License(name="Personal License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = i18n_patterns(
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=60 * 5),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=60 * 5),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$",
        schema_view.with_ui("redoc", cache_timeout=60 * 5),
        name="schema-redoc",
    ),
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
                    "calf/convert-to-adult/",
                    ConvertToAdultView.as_view(),
                    name="convert_to_adult",
                ),
                path(
                    "latest-geolocs/",
                    SimpleGroupedGeolocationsView.as_view(),
                    name="latest_grouped_geolocations",
                ),
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
                    "events/breedingstock/measurements/<int:single_event_pk>/",
                    BreedingStockMeasurementView.as_view(),
                ),
                path(
                    "events/breedingstock/measurements/",
                    BreedingStockMeasurementView.as_view(),
                ),
                path(
                    "events/calf/measurements/<int:single_event_pk>/",
                    CalfMeasurementView.as_view(),
                ),
                path("events/calf/measurements/", CalfMeasurementView.as_view(),),
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
                path(
                    "notifications/mark-as-read/<int:pk>/",
                    NotificationMarkAsReadView.as_view(),
                ),
                path("usersupport/", SupportTicketCreateView.as_view()),
            ]
            + router.urls
        ),
    ),
    path("api-token-auth/", CustomAuthToken.as_view()),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    re_path(r"^$", RedirectView.as_view(url=reverse_lazy("api-root"), permanent=False)),
    # If no prefix is given, use the default language
    prefix_default_language=False,
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
