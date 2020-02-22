from django.contrib import admin

from .models import ImageryRequest

# Register your models here.

@admin.register(ImageryRequest)
class ImageryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'cadastre', 'farm', 'process_status',
                    'created_date', 'requested_date', 'actual_date')
    list_filter = ('process_status', 'created_date', 'requested_date', 'actual_date')
    date_hierarchy = 'created_date'
    search_fields = ['id', '=cadastre__cad_number',]
    exclude = ('process_status', 'generate_bands', 'created_date', 'requested_date', 'actual_date', 'results_dir',)
