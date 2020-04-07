from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import connections
from ..celery import app

# from .models import ImageryRequest
# from .serializers import ImageryRequestSerializer
from tumar.animals.models import Cadastre

# Create your views here.


class RequestIndicatorsView(APIView):
    def post(self, request):
        if "cad_number" not in request.data:
            return Response(
                {"error": "Provide cad_number"}, status=status.HTTP_404_NOT_FOUND
            )

        if not Cadastre.objects.filter(
            farm__user=self.request.user, cad_number=request.data["cad_number"]
        ).exists():
            return Response(
                {"fail": "Cadastre with this cad_number does not belong to you"},
                status=status.HTTP_404_NOT_FOUND,
            )

        egistic_cadastre_id = None
        target_dates = None

        try:
            with connections["egistic_2"].cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM cadastres_cadastre WHERE kad_nomer = %s",
                    [request.data["cad_number"]],
                )
                row = cursor.fetchone()
                egistic_cadastre_id = row[0]
        except TypeError:
            return Response(
                {
                    "fail": "Cadastre number was not found in the egistic database."
                    + " Imagery for custom geometries is not supported yet."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if "requested_date" in request.data:
            target_dates = [
                request.data["requested_date"],
            ]

        result = app.signature(
            "process_cadastres",
            kwargs={
                "param_values": dict(param="id", values=[egistic_cadastre_id]),
                "target_dates": target_dates,
                "days_range": 14,
            },
            queue="process_cadastres",
            priority=5,
        )
        result.delay()

        return Response({"success": True}, status=status.HTTP_201_CREATED)


class LatestIndicatorsView(APIView):
    def get(self, request, cad_number):
        # cad_number = request.query_params.get("cad_number", None)
        # if cad_number is None:
        #     return Response(
        #         {
        #             "error": "cadastre number was not specified:"
        #             + " 'baseURL'/indicators/latest/?cad_number=<cad_number:int>"
        #         },
        #         status=status.HTTP_404_NOT_FOUND,
        #     )

        cadastre = get_object_or_404(
            Cadastre, farm__user=self.request.user, cad_number=cad_number
        )
        egistic_cadastre_id = None
        response_data = {"cadastre_response": {}, "cadastre_images": {}}

        try:
            with connections["egistic_2"].cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM cadastres_cadastre WHERE kad_nomer = %s",
                    [cadastre.cad_number],
                )
                row = cursor.fetchone()
                egistic_cadastre_id = row[0]
        except TypeError:
            return Response(
                {
                    "fail": "Cadastre number was not found in the egistic database."
                    + " Imagery for custom geometries is not supported yet."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch imagery
        try:
            with connections["egistic_2"].cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM tumar_cadastreresult WHERE cadastre_id = %s ORDER BY"
                    + " actual_date DESC",
                    [egistic_cadastre_id],
                )
                row = cursor.fetchone()
                response_data["cadastre_response"] = {
                    "id": row[0],
                    "ndvi": row[1],
                    "gndvi": row[2],
                    "clgreen": row[3],
                    "ndmi": row[4],
                    "ndsi": row[5],
                    "actual_date": row[6],
                    "results_dir": row[7],
                    "cadastre_id": row[8],
                    "is_layer_created": row[9],
                }
        except TypeError:
            return Response(
                {"fail": "Imagery tiffs was not found in the database or not finished"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch PNGs
        try:
            with connections["egistic_2"].cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM tumar_cadastreresultimage WHERE"
                    + " cadastreresult_id = %s",
                    [response_data["cadastre_response"][0]],
                )
                row = cursor.fetchone()
                response_data["cadastre_images"] = {
                    "id": row[0],
                    "ndvi": row[1],
                    "gndvi": row[2],
                    "clgreen": row[3],
                    "ndmi": row[4],
                    "rgb": row[5],
                    "cadastreresult_id": row[6],
                }
        except TypeError:
            return Response(
                {"fail": "Imagery PNGs were not found in the database or not finished"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(response_data)
