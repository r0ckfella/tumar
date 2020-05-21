from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from tumar.animals.models import Cadastre

from ..animals.serializers import CadastreImageryRequestSerializer
from .exceptions import (
    ImageryRequestAlreadyExistsError,
    FreeRequestsExpiredError,
    CadastreNotInEgisticError,
)
from .models import ImageryRequest

# Create your views here.


class RequestIndicatorsView(APIView):
    def post(self, request):
        if "cadastre_id" not in request.data:
            return Response(
                {"error": "Provide cadastre id"}, status=status.HTTP_404_NOT_FOUND
            )

        the_cadastre = get_object_or_404(
            Cadastre, pk=request.data["cadastre_id"], farm__user=request.user
        )

        ir = None
        try:
            ir = ImageryRequest(cadastre=the_cadastre)
            if "requested_date" in request.data:
                ir.requested_date = request.data["requested_date"]
            ir.save()
        except ImageryRequestAlreadyExistsError:
            return Response(
                {
                    "error": (
                        "Imagery Request for this requested date {} already exists."
                    ).format(ir.requested_date)
                },
                status=status.HTTP_409_CONFLICT,
            )

        try:
            ir.start_image_processing()
        except FreeRequestsExpiredError:
            return Response(
                {"error": "You used all free requests for image processing."},
                status=status.HTTP_409_CONFLICT,
            )
        except CadastreNotInEgisticError:
            return Response(
                {
                    "error": (
                        "This cadastre with cad_number {}" " is not in egistic db"
                    ).format(the_cadastre.cad_number)
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"imageryrequest_id": ir.pk, "requested_date": ir.requested_date},
            status=status.HTTP_201_CREATED,
        )


class LatestIndicatorsView(APIView):
    def get(self, request):
        valid_query_params = ("cadastre_id",)

        if not all(
            param in valid_query_params for param in tuple(request.query_params.keys())
        ):
            return Response(
                {"valid query params": valid_query_params},
                status=status.HTTP_404_NOT_FOUND,
            )

        cadastre_id = request.query_params.get("cadastre_id", None)
        the_farm = request.user.farm

        qs = None
        if cadastre_id:
            qs = Cadastre.objects.filter(farm=the_farm, pk=cadastre_id)
        else:
            qs = Cadastre.objects.filter(farm=the_farm)

        serializer = CadastreImageryRequestSerializer(qs, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
