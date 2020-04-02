from django.contrib import admin

from .models import CompanyDirection, Company, City

# Register your models here.


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass


@admin.register(CompanyDirection)
class CompanyDirectionAdmin(admin.ModelAdmin):
    pass
