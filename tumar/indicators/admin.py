from django.contrib import admin

from .models import ImageryRequest

# Register your models here.


@admin.register(ImageryRequest)
class ImageryRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cadastre",
        "status",
        "created_at",
        "requested_date",
        "finished_at",
    )
    list_filter = (
        "status",
        "created_at",
        "requested_date",
        "finished_at",
    )
    date_hierarchy = "created_at"
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
        "created_at",
        "finished_at",
    )
