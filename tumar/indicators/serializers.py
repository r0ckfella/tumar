from rest_framework import serializers

from .models import ImageryRequest


class ImageryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageryRequest
        fields = (
            "id",
            "status",
            "created_at",
            "requested_date",
            "finished_at",
            "ndvi",
            "gndvi",
            "clgreen",
            "ndmi",
            "ndsi",
            "results_dir",
            "ndvi_dir",
            "gndvi_dir",
            "clgreen_dir",
            "ndmi_dir",
            "rgb_dir",
            "is_layer_created",
        )
