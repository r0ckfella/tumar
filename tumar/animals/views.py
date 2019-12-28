from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import utils
from .filters import AnimalPathFilter
from .models import Farm, Animal, Geolocation, Machinery, Event
from .serializers import FarmSerializer, GeolocationAnimalSerializer, EventAnimalSerializer, AnimalSerializer, \
    MachinerySerializer


# Create your views here.

class FarmViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves farms
    """
    queryset = Farm.objects.all().order_by('iin')
    serializer_class = FarmSerializer


class AnimalFarmViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves animals and their farm
    """
    queryset = Animal.objects.all().order_by('imei')
    serializer_class = AnimalSerializer


class MachineryFarmViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves machinery and their farm
    """
    queryset = Machinery.objects.all().order_by('machinery_code')
    serializer_class = MachinerySerializer


class GeolocationAnimalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves geolocations and their animal
    """
    queryset = Geolocation.geolocations.all().order_by('animal__imei', '-time')
    serializer_class = GeolocationAnimalSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('animal__imei', 'time',)


class EventAnimalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves events and their animal
    """
    queryset = Event.objects.all().order_by('animal__imei', '-time')
    serializer_class = EventAnimalSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('animal__imei',)


class GetAnimalPath(APIView):
    """
    View to get the path of an animal between two dates (time included).
    """

    def get(self, request):
        """
        Return a Linestring(GeoJSON) of the path.

        url example: {baseURL}/api/v1/get-path/?imei=869270046995022&time_before=2019-12-03 00:00:00
        """
        valid_query_params = ('imei', 'time_after', 'time_before',)
        queryset = Geolocation.geolocations.all().order_by('time')

        if not request.GET or not all(param in valid_query_params for param in tuple(request.query_params.keys())):
            return Response({"valid query params": valid_query_params}, status=status.HTTP_404_NOT_FOUND)

        filtered_data = AnimalPathFilter(request.GET, queryset=queryset)

        linestring = utils.get_linestring_from_geolocations(filtered_data.qs)

        return Response(linestring.geojson)  # Any Python primitive is ok, linestring.geojson is str fyi
