from django.contrib import admin
from utils.admin import auto_fieldset, readonly_fields

from .models import Award, Book


class AuthorNameMixin:
    """Mixin to provide author name display method."""

    def author_name(self, obj):
        return obj.author.name

    author_name.short_description = "Author"


class AwardAdmin(AuthorNameMixin, admin.ModelAdmin):
    list_display = ("id", "name", "year_awarded", "author_name", "view_count")
    search_fields = (
        "name",
        "year_awarded",
        "author__first_name",
        "author__last_name",
        "id",
    )
    list_filter = ("year_awarded", "author__first_name", "author__last_name")
    ordering = ("-year_awarded", "view_count")
    readonly_fields = readonly_fields

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "year_awarded", "author"),
            },
        ),
        (
            "Details",
            {
                "fields": ("description",),
            },
        ),
        auto_fieldset,
    )


class BookAdmin(AuthorNameMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "isbn",
        "date_published",
        "author_name",
        "view_count",
    )
    search_fields = ("title", "isbn", "date_published", "id")
    list_filter = (
        "date_published",
        "author__first_name",
        "author__last_name",
        "language",
        "rating",
    )
    ordering = ("-date_published", "rating", "view_count")
    readonly_fields = readonly_fields

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "author", "date_published", "rating"),
            },
        ),
        (
            "Details",
            {
                "fields": ("isbn", "pages", "cover_image", "summary"),
            },
        ),
        auto_fieldset,
    )


admin.site.register(Book, BookAdmin)
admin.site.register(Award, AwardAdmin)
