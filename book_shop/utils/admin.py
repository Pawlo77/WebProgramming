readonly_fields = (
    "created_by",
    "date_created",
    "updated_by",
    "date_updated",
    "id",
    "view_count",
)

auto_fieldset = (
    "System",
    {
        "fields": (
            "created_by",
            "date_created",
            "updated_by",
            "date_updated",
            "id",
            "view_count",
        ),
        "classes": ("collapse",),
    },
)
