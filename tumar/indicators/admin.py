from django.contrib import admin

from .models import ImageryRequest
from .choices import PENDING

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
    actions = [
        "start_image_processing",
    ]

    def start_image_processing(self, request, queryset):
        started = []
        not_started = []

        for ir in queryset:
            if ir.status == PENDING:
                ir.start_image_processing(disable_check=True)
                started.append(ir.pk)
            else:
                not_started.append(ir.pk)

        self.message_user(
            request,
            "{} успешно запущены.\n{} не запущены.".format(started, not_started),
        )

    start_image_processing.short_description = (
        "Start image processing for selected requests"
    )
