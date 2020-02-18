from rest_framework import serializers

from .models import ImageryRequest


class ImageryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageryRequest
        fields = ('id', 'farm', 'cadastre', 'generate_bands', 'process_status',
                  'created_date', 'actual_date', 'requested_date', 'results_dir',)
        extra_kwargs = {
            'requested_date': {'write_only': True, 'required': True},
            'farm': {'read_only': True},
            'created_date': {'read_only': True},
            'actual_date': {'read_only': True},
            'results_dir': {'read_only': True},
        }
