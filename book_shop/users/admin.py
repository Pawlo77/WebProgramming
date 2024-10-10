from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateRangeFilterBuilder

from .models import CustomUser

User = get_user_model()


@admin.action(description="Deactivate selected users")
def deactivate_users(modeladmin, request, queryset):
    queryset.update(is_active=False)
    modeladmin.message_user(
        request, f"{queryset.count()} user(s) were successfully deactivated."
    )


class CustomUserAdmin(UserAdmin):
    actions = [deactivate_users]
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "role",
        "education",
        "date_of_birth",
        "date_joined",
        "is_active",
    )
    search_fields = ("email", "first_name", "last_name", "id")
    list_filter = (
        "role",
        "education",
        "is_active",
        (
            "date_joined",
            DateRangeFilterBuilder(
                title="Date Joined",
            ),
        ),
        (
            "date_of_birth",
            DateRangeFilterBuilder(
                title="Date of birth",
            ),
        ),
    )
    ordering = ("-date_joined", "id")
    readonly_fields = ("date_joined", "date_updated", "id")
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "date_of_birth")}),
        ("Role Info", {"fields": ("role", "education")}),
        (
            "Permissions",
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
        ("System", {"fields": ("date_joined", "date_updated", "id")}),
    )

    add_fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "date_of_birth")}),
        ("Role Info", {"fields": ("role", "education")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
