from django.db.models import OuterRef, Subquery, Sum, FloatField
from django.db.models.functions import Cast

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
from ..ecalendar.models import SingleCalfEvent


class AnimalCountByTypeView(APIView):
    def get(self, request):
        the_farm = request.user.farm

        response_data = {
            "Коровы": the_farm.breedingstock_count,
            "Молодняк до 12 месяцев": the_farm.calf_set.less_12_months_count(),
            "Молодняк после 12 месяцев": the_farm.calf_set.greater_12_months_count(),
            "Племенные быки": the_farm.breedingbull_count,
            "Нетели (беременные телки)": the_farm.breedingstock_set.pregnant_count(),
        }

        return Response(response_data, status=status.HTTP_200_OK)


class CalfToCowsRatioView(APIView):
    def get(self, request):
        the_farm = request.user.farm

        response_data = {
            "Выход телят": the_farm.calves_count / the_farm.breedingstock_count * 100,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class PastureToAnimalRatioView(APIView):
    def get(self, request):
        the_farm = request.user.farm

        response_data = {
            "Обеспеченность пастбищами (га/голову)": the_farm.total_pastures_area_in_ha
            / the_farm.total_animal_count,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class BirthWeightAverageView(APIView):
    def get(self, request):
        the_farm = request.user.farm

        birth_event = (
            SingleCalfEvent.objects.filter(
                event__title__icontains="отел", completed=True
            )
            .filter(animal=OuterRef("pk"))
            .order_by("completion_date")
        )
        annote_query = Subquery(
            birth_event.values("event__attributes__birth_weight")[:1]
        )

        sum_birth_weight = (
            the_farm.calf_set.filter(active=True)
            .annotate(birth_weight_str=annote_query)
            .annotate(birth_weight=Cast("birth_weight_str", output_field=FloatField()))
            .aggregate(total_sum=Sum("birth_weight"))["total_sum"]
        )

        response_data = {
            "Лёгкость отела (кг)": sum_birth_weight / the_farm.calves_count,
        }

        return Response(response_data, status=status.HTTP_200_OK)
