from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include, reverse_lazy
from django.views.generic.base import RedirectView
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .animals.views import FarmViewSet, GeolocationAnimalViewSet, AnimalFarmViewSet, GetAnimalPath
from .users.views import UserViewSet, UserCreateViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)
router.register(r'farms', FarmViewSet)
router.register(r'animals', AnimalFarmViewSet)
router.register(r'geolocations', GeolocationAnimalViewSet)

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),

    # Custom API endpoints
    path('api/v1/', include([path('get-path/', GetAnimalPath.as_view(), name='get_path'),
                             ] + router.urls)),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

    # If no prefix is given, use the default language
    prefix_default_language=False
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
