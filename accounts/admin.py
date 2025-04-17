from .models import CustomUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser

    # Fields to display in admin user list
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
    )

    # Fieldsets for viewing and editing user objects
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
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

    # Fieldsets for the "add user" form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "password1", "password2"),
            },
        ),
    )

    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
