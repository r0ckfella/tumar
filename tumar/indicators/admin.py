from django.contrib import admin

from .models import ImageryRequest

# Register your models here.


@admin.register(ImageryRequest)
class ImageryRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cadastre",
        "status",
        "created_date",
        "requested_date",
        "actual_date",
    )
    list_filter = (
        "process_status",
        "created_date",
        "requested_date",
        "actual_date",
    )
    date_hierarchy = "created_date"
    search_fields = (
        "id",
        "cadastre",
        "=cadastre__cad_number",
    )
    exclude = (
        "ndvi",
        "gndvi",
        "clgreen",
        "ndmi",
        "ndsi",
        "is_layer_created",
    )
    readonly_fields = (
        "results_dir",
        "status",
        "created_date",
        "actual_date",
    )
