from rest_framework import serializers

from .models import Company, CompanyDirection


class CompanyDirectionSerializer(serializers.ModelSerializer):
    companies_num = serializers.SerializerMethodField()

    class Meta:
        model = CompanyDirection
        fields = (
            "id",
            "title",
            "companies_num",
        )

    def get_companies_num(self, obj):
        return obj.companies.count()


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
