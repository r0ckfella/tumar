from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Company, CompanyDirection
from .serializers import (
    CompanyListSerializer,
    CompanyDirectionSerializer,
    CompanySerializer,
)


# Create your views here.


class CompanyDirectionListView(APIView):
    def get(self, request):
        all_directions = CompanyDirection.objects.all().order_by("id")
        serializer = CompanyDirectionSerializer(all_directions, many=True)

        return Response(serializer.data)


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Lists and retrieves companies
    """

    queryset = Company.objects.all().order_by("id")
    model = Company
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ("directions",)

    def get_serializer_class(self):
        serializers_class_map = {
            "retrieve": CompanySerializer,
            "list": CompanyListSerializer,
        }

        return serializers_class_map.get(self.action)
