from rest_framework import viewsets
from rest_framework.permissions import AllowAny

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
    queryset = Animal.objects.all()
    serializer_class = AnimalFarmSerializer
    permission_classes = (AllowAny,)


class GeolocationAnimalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves geolocations and their animal
    """
    queryset = Geolocation.objects.all().order_by('id')
    serializer_class = GeolocationAnimalSerializer
    permission_classes = (AllowAny,)
