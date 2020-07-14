import datetime

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CalfEvent,
    BreedingStockEvent,
    SingleBreedingStockEvent,
    SingleCalfEvent,
)
from .serializers import (
    CalfEventSerializer,
    BreedingStockEventSerializer,
    BreedingStockMeasurementSerializer,
    CalfMeasurementSerializer,
)

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
            BreedingStockEvent.objects.filter(farm__user=self.request.user)
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
            CalfEvent.objects.filter(farm__user=self.request.user)
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


class BreedingStockMeasurementView(APIView):
    def get(self, request):
        animal_pk = request.query_params.get("animal_pk", None)

        if not animal_pk:
            return Response(
                {"error": "?animal_pk=<id> should be set in the URL"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            SingleBreedingStockEvent.objects.filter(animal=animal_pk)
            .filter(
                Q(event__title__icontains="скт")
                | Q(event__title__icontains="взвешивание")
                | Q(event__title__icontains="отел")
            )
            .order_by("-completion_date", "event__title")
        )

        serializer = BreedingStockMeasurementSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BreedingStockMeasurementSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, single_event_pk):
        s_event = get_object_or_404(SingleBreedingStockEvent, pk=single_event_pk)

        serializer = BreedingStockMeasurementSerializer(
            s_event, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, single_event_pk):
        s_event = get_object_or_404(SingleBreedingStockEvent, pk=single_event_pk)
        s_event.delete()
        return Response({"deleted": True}, status=status.HTTP_204_NO_CONTENT)


class CalfMeasurementView(APIView):
    def get(self, request):
        animal_pk = request.query_params.get("animal_pk", None)

        if not animal_pk:
            return Response(
                {"error": "?animal_pk=<id> should be set in the URL"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = (
            SingleCalfEvent.objects.filter(animal=animal_pk)
            .filter(
                Q(event__title__icontains="скт")
                | Q(event__title__icontains="отел")
                | Q(event__title__icontains="отъем")
                | Q(event__title__icontains="взвешивание")
            )
            .order_by("-completion_date", "event__title")
        )

        serializer = CalfMeasurementSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CalfMeasurementSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, single_event_pk):
        s_event = get_object_or_404(SingleCalfEvent, pk=single_event_pk)

        serializer = CalfMeasurementSerializer(s_event, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, single_event_pk):
        s_event = get_object_or_404(SingleCalfEvent, pk=single_event_pk)
        s_event.delete()
        return Response({"deleted": True}, status=status.HTTP_204_NO_CONTENT)
