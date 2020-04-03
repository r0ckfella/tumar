from rest_framework import serializers

from .models import Company, CompanyDirection


class CompanyDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDirection
        fields = (
            "id",
            "title",
        )


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "title",
        )


class CompanySerializer(serializers.ModelSerializer):
    directions = CompanyDirectionSerializer(many=True, read_only=True)
    cities = serializers.StringRelatedField(many=True)

    class Meta:
        model = Company
        fields = "__all__"
