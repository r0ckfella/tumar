from datetime import datetime as dt

import django.utils.timezone as tz
import pytz
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import utils
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
    queryset = Geolocation.geolocations.all().order_by('time')
    serializer_class = GeolocationAnimalSerializer
    permission_classes = (AllowAny,)


class GetAnimalPath(APIView):
    """
    View to get the path of an animal between two dates (time included).
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        """
        Return a Linestring(GeoJSON) of the path.
        """
        my_tz = pytz.timezone('Asia/Almaty')
        start_time = dt.strptime(request.data['start_time'], "%Y-%m-%d %H:%M:%S")
        start_time_aware = tz.make_aware(start_time, my_tz)
        end_time = dt.strptime(request.data['end_time'], "%Y-%m-%d %H:%M:%S")
        end_time_aware = tz.make_aware(end_time, my_tz)

        geolocations_qs = Geolocation.geolocations.get_path(animal_imei=request.data['animal_imei'],
                                                            start_time=start_time_aware,
                                                            end_time=end_time_aware)

        linestring = utils.get_linestring_from_geolocations(geolocations_qs)

        return Response(linestring.geojson)  # Any Python primitive is ok, linestring.geojson is str
