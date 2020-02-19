from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import Http404
from django.shortcuts import render

from .models import ImageryRequest
from .serializers import ImageryRequestSerializer
from tumar.animals.models import Cadastre, Farm

# Create your views here.


class RequestIndicatorsView(APIView):
    def post(self, request):
        user_farm = get_object_or_404(Farm, user=self.request.user)

        serializer = ImageryRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(farm=user_farm)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LatestIndicatorsView(APIView):
    def get(self, request):
        cad_number = request.query_params.get('cad_number', None)
        if cad_number is None:
            return Response({"error": "cadastre number was not specified: 'baseURL'/indicators/latest/?cad_number=<cad_number:int>"}, status=status.HTTP_404_NOT_FOUND)

        cadastre = get_object_or_404(Cadastre, farm__user=self.request.user, cad_number=cad_number)

        try:
            latest_imagery_request = ImageryRequest.objects.filter(
                farm__user=self.request.user, cadastre=cadastre, results_dir__isnull=False, actual_date__isnull=False).latest('actual_date')
        except ImageryRequest.DoesNotExist:
            raise Http404

        serializer = ImageryRequestSerializer(latest_imagery_request)

        return Response(serializer.data)
