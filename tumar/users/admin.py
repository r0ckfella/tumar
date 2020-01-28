from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_active',)

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('image',)}),
    )


admin.site.unregister(Group)
