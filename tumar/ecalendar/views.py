from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from tumar.animals.models import BreedingStock
from .models import CalfEvent, BreedingStockEvent
from .serializers import CalfEventSerializer, BreedingStockEventSerializer
from .utils import create_mother_cow_events_next_year
# Create your views here.


class BreedingStockEventViewSet(viewsets.ModelViewSet):
    """
    Lists and retrieves events and their animal
    """
    queryset = BreedingStockEvent.objects.all().order_by('animal__id', '-scheduled_date')
    serializer_class = BreedingStockEventSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('animal__id',)


class CalfEventViewSet(viewsets.ModelViewSet):
    """
    Lists and retrieves events and their animal
    """
    queryset = CalfEvent.objects.all().order_by('animal__id', '-scheduled_date')
    serializer_class = CalfEventSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('animal__id',)


class NextYearBreedingStockEventView(APIView):
    def post(self, request):
        cow = get_object_or_404(BreedingStock, id=request.data["id"])

        try:
            create_mother_cow_events_next_year(cow)
        except Exception as e:
            print(e)
            return Response({"error": "found the cow, but could not create events for it"},
                            status=status.HTTP_201_CREATED)
        return Response({"success": "standard next year events for cow created"},
                        status=status.HTTP_400_BAD_REQUEST) 

