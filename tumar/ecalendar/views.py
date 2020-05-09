from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from tumar.animals.models import BreedingStock, Calf, FEMALE, MALE
from .models import CalfEvent, BreedingStockEvent
from .serializers import CalfEventSerializer, BreedingStockEventSerializer
from .utils import create_mother_cow_events_next_year

# Create your views here.


class BreedingStockEventViewSet(viewsets.ModelViewSet):
    """
    Lists and retrieves events and their animal
    """

    serializer_class = BreedingStockEventSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("animal__id",)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return BreedingStockEvent.objects.all().order_by(
                "animal__id", "-scheduled_date_range"
            )
        return BreedingStockEvent.objects.filter(
            animal__farm__user=self.request.user
        ).order_by("animal__id", "-scheduled_date_range")


class CalfEventViewSet(viewsets.ModelViewSet):
    """
    Lists and retrieves events and their animal
    """

    # queryset = CalfEvent.objects.all().order_by('animal__id', '-scheduled_date_range')
    serializer_class = CalfEventSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("animal__id",)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CalfEvent.objects.all().order_by(
                "animal__id", "-scheduled_date_range"
            )
        return CalfEvent.objects.filter(animal__farm__user=self.request.user).order_by(
            "animal__id", "-scheduled_date_range"
        )


class NextYearBreedingStockEventView(APIView):
    def post(self, request):
        cow = get_object_or_404(BreedingStock, id=request.data["id"])

        try:
            create_mother_cow_events_next_year(cow)
        except Exception as e:
            print(e)
            return Response(
                {"error": "found the cow, but could not create events for it"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"success": "standard next year events for cow created"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class AllBreedingStockEventView(APIView):
    def get(self, request, pk):
        if self.request.user.is_superuser:
            cow = get_object_or_404(BreedingStock, id=pk)
        else:
            cow = get_object_or_404(BreedingStock, id=pk, farm__user=self.request.user)
        serializer = BreedingStockEventSerializer(cow.events, many=True)

        return Response(serializer.data)


class AllCalfEventView(APIView):
    def get(self, request, pk):
        if self.request.user.is_superuser:
            calf = get_object_or_404(Calf, id=pk)
        else:
            calf = get_object_or_404(Calf, id=pk, farm__user=self.request.user)
        serializer = CalfEventSerializer(calf.events, many=True)

        return Response(serializer.data)


class CalendarView(APIView):
    def get(self, request, pk):
        if self.request.user.is_superuser:
            cow = get_object_or_404(BreedingStock, id=pk)
        else:
            cow = get_object_or_404(BreedingStock, id=pk, farm__user=self.request.user)

        female_calves = cow.calves.filter(gender=FEMALE)
        male_calves = cow.calves.filter(gender=MALE)

        data = {
            "cow": {"id": cow.id, "name": cow.name, "events": []},
            "male_calves": [],
            "female_calves": [],
        }

        cow_serializer = BreedingStockEventSerializer(
            cow.events.order_by("scheduled_date_range"), many=True
        )
        data["cow"]["events"] = cow_serializer.data

        for calf in female_calves:
            calf_serializer = CalfEventSerializer(
                calf.events.order_by("scheduled_date_range"), many=True
            )
            data["female_calves"].append(
                {"id": calf.id, "name": calf.name, "events": []}
            )
            data["female_calves"][-1]["events"] = calf_serializer.data

        for calf in male_calves:
            calf_serializer = CalfEventSerializer(
                calf.events.order_by("scheduled_date_range"), many=True
            )
            data["male_calves"].append({"id": calf.id, "name": calf.name, "events": []})
            data["male_calves"][-1]["events"] = calf_serializer.data

        return Response(data)
