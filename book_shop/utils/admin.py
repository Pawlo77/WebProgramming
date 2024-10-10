from django.contrib import admin

readonly_fields = ("created_by", "date_created", "updated_by", "date_updated", "id")
auto_fieldset = (
    "System",
    {
        "fields": ("created_by", "date_created", "updated_by", "date_updated", "id"),
        "classes": ("collapse",),
    },
)
