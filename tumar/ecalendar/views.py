import datetime

from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from tumar.animals.models import BreedingStock, Calf, FEMALE, MALE
from .models import (
    CalfEvent,
    BreedingStockEvent,
    SingleBreedingStockEvent,
    SingleCalfEvent,
)
from .serializers import CalfEventSerializer, BreedingStockEventSerializer
from .utils import create_mother_cow_events_next_year

# Create your views here.


class BreedingStockEventViewSet(viewsets.ModelViewSet):
    """
    Lists and retrieves events and their animal
    """

    serializer_class = BreedingStockEventSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ("animals__id",)
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_superuser:
            return BreedingStockEvent.objects.all().order_by("-scheduled_date_range")
        return (
            BreedingStockEvent.objects.filter(animals__farm__user=self.request.user)
            .distinct()
            .order_by("-scheduled_date_range")
        )


class ToggleBreedingStockEventView(APIView):
    def patch(self, request, event_pk, animal_pk):
        completion_date = request.data.get("completion_date", None)
        attributes = request.data.get("attributes", None)

        if request.user.is_superuser:
            single_bs_event = get_object_or_404(
                SingleBreedingStockEvent, animal=animal_pk, event=event_pk
            )
        else:
            single_bs_event = get_object_or_404(
                SingleBreedingStockEvent,
                event=event_pk,
                animal=animal_pk,
                animal__farm__user=request.user,
            )

        single_bs_event.completed = not single_bs_event.completed

        if completion_date:
            single_bs_event.completion_date = datetime.datetime.strptime(
                completion_date, "%d-%m-%Y"
            ).date()
        else:
            single_bs_event.completion_date = datetime.date.today()

        if single_bs_event.attributes is None:
            single_bs_event.attributes = {}

        for key, value in attributes.items():
            single_bs_event.attributes[key] = value

        single_bs_event.save()

        return Response(
            {"success": True, "completed": single_bs_event.completed},
            status=status.HTTP_201_CREATED,
        )


class CalfEventViewSet(viewsets.ModelViewSet):
    """
    Lists and retrieves events and their animal
    """

    # queryset = CalfEvent.objects.all().order_by('animal__id', '-scheduled_date_range')
    serializer_class = CalfEventSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ("animal__id",)
    pagination_class = None

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CalfEvent.objects.all().order_by("-scheduled_date_range")
        return (
            CalfEvent.objects.filter(animals__farm__user=self.request.user)
            .distinct()
            .order_by("-scheduled_date_range")
        )


class ToggleCalfEventView(APIView):
    def patch(self, request, event_pk, animal_pk):
        completion_date = request.data.get("completion_date", None)
        attributes = request.data.get("attributes", None)

        if request.user.is_superuser:
            single_calf_event = get_object_or_404(
                SingleCalfEvent, animal=animal_pk, event=event_pk
            )
        else:
            single_calf_event = get_object_or_404(
                SingleCalfEvent,
                event=event_pk,
                animal=animal_pk,
                animal__farm__user=request.user,
            )

        single_calf_event.completed = not single_calf_event.completed

        if completion_date:
            single_calf_event.completion_date = datetime.datetime.strptime(
                completion_date, "%d-%m-%Y"
            ).date()
        else:
            single_calf_event.completion_date = datetime.date.today()

        if single_calf_event.attributes is None:
            single_calf_event.attributes = {}

        for key, value in attributes.items():
            single_calf_event.attributes[key] = value

        single_calf_event.save()

        return Response(
            {"success": True, "completed": single_calf_event.completed},
            status=status.HTTP_201_CREATED,
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
