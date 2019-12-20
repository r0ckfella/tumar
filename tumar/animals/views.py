from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import utils
from .filters import AnimalPathFilter
from .models import Farm, Animal, Geolocation
from .serializers import FarmSerializer, AnimalFarmSerializer, GeolocationAnimalSerializer


# Create your views here.

class FarmViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves farms
    """
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = (AllowAny,)


class AnimalFarmViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves animals and their farm
    """
    queryset = Animal.objects.all().order_by('imei')
    serializer_class = AnimalFarmSerializer
    permission_classes = (AllowAny,)


class GeolocationAnimalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves geolocations and their animal
    """
    queryset = Geolocation.geolocations.all().order_by('animal__imei', '-time')
    serializer_class = GeolocationAnimalSerializer
    permission_classes = (AllowAny,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('animal__imei',)


class GetAnimalPath(APIView):
    """
    View to get the path of an animal between two dates (time included).
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        """
        Return a Linestring(GeoJSON) of the path.

        url example: /api/v1/get-path/?imei=869270046995022&time_before=2019-12-03 00:00:00
        """
        valid_query_params = ('imei', 'time_after', 'time_before',)
        queryset = Geolocation.geolocations.none()  # return empty QuerySet if there are no query params

        if request.GET and all(param in valid_query_params for param in tuple(request.query_params.keys())):
            queryset = Geolocation.geolocations.all().order_by(
                'time')  # return all objects if query params are present and valid
        else:
            return Response({"valid query params": valid_query_params}, status=status.HTTP_404_NOT_FOUND)

        filtered_data = AnimalPathFilter(request.GET, queryset=queryset)

        linestring = utils.get_linestring_from_geolocations(filtered_data.qs)

        return Response(linestring.geojson)  # Any Python primitive is ok, linestring.geojson is str
