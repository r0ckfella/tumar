from typing import Set


from django.contrib.auth.admin import UserAdmin
from django.contrib.gis import admin
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )

    readonly_fields = (
        "date_joined",
        "last_login",
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "image")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("image",)}),)

    def has_delete_permission(self, request, obj=None):
        """
        When obj is None, the user requested the list view.
        When obj is not None, the user requested the change view of a specific instance.
        """
        return (
            request.user.is_superuser
            or request.user.groups.filter(name="Поддержка").exists()
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()  # type: Set[str]

        if not is_superuser:
            disabled_fields |= {
                "username",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            }

        # Prevent non-superusers from editing their own permissions
        if not is_superuser and obj is not None and obj == request.user:
            disabled_fields |= {
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form


admin.site.unregister(Site)
