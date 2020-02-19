from rest_framework import serializers

from .models import ImageryRequest


class ImageryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageryRequest
        fields = ('id', 'farm', 'cadastre', 'process_status',
                  'created_date', 'actual_date', 'requested_date', 'results_dir',)
        extra_kwargs = {
            'id': {'read_only': True},
            'farm': {'read_only': True},
            'process_status': {'read_only': True},
            'created_date': {'read_only': True},
            'actual_date': {'read_only': True},
            'requested_date': {'required': True},
            'results_dir': {'read_only': True},
        }
