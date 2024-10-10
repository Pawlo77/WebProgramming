from django.contrib import admin
from django.db import models
from django.db.models import Count, Max
from rangefilter.filters import DateRangeFilterBuilder
from utils.admin import auto_fieldset, readonly_fields

from .models import Author, Critic


@admin.action(description="Reset View Count")
def reset_view_count(modeladmin, request, queryset):
    queryset.update(view_count=0)
    modeladmin.message_user(
        request, f"{queryset.count()} person(s) were successfully reset."
    )


class PopularityFilter(admin.SimpleListFilter):
    title = "Popularity"
    parameter_name = "popularity"

    def lookups(self, request, model_admin):
        return [
            ("low", "Low (0-3)"),
            ("medium", "Medium (4-6)"),
            ("high", "High (7-10)"),
        ]

    def queryset(self, request, queryset):
        max_views = (
            Author.objects.aggregate(max_views=Max("view_count"))["max_views"] or 1
        )  # Avoid division by zero
        queryset = queryset.annotate(
            popularity_score=(models.F("view_count") / max_views) * 10
        )

        if self.value() == "low":
            return queryset.filter(popularity_score__lte=3)
        if self.value() == "medium":
            return queryset.filter(popularity_score__gt=3, popularity_score__lte=6)
        if self.value() == "high":
            return queryset.filter(popularity_score__gt=6)

        return queryset


class PublishedFilter(admin.SimpleListFilter):
    title = "Has Published"
    parameter_name = "has_published"

    def lookups(self, request, model_admin):
        return [
            ("published", "Has Published"),
            ("not_published", "Not Published"),
        ]

    def queryset(self, request, queryset):
        queryset = queryset.annotate(publications_count=Count("books"))

        if self.value() == "published":
            return queryset.filter(publications_count__gt=0)
        if self.value() == "not_published":
            return queryset.filter(publications_count=0)

        return queryset


class AwardedFilter(admin.SimpleListFilter):
    title = "Awarded"
    parameter_name = "awarded"

    def lookups(self, request, model_admin):
        return [
            ("awarded", "Awarded"),
            ("not_awarded", "Not Awarded"),
        ]

    def queryset(self, request, queryset):
        queryset = queryset.annotate(awards_count=Count("awards"))

        if self.value() == "awarded":
            return queryset.filter(awards_count__gt=0)
        if self.value() == "not_awarded":
            return queryset.filter(awards_count=0)

        return queryset


class AliveFilter(admin.SimpleListFilter):
    title = "Alive"
    parameter_name = "alive"

    def lookups(self, request, model_admin):
        return [
            ("alive", "Alive"),
            ("deceased", "Deceased"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "alive":
            return queryset.filter(death_date__isnull=True)
        if self.value() == "deceased":
            return queryset.filter(death_date__isnull=False)

        return queryset


class DisplayAliveMixin:
    """Mixin to add alive status display to admin classes."""

    def display_alive(self, obj):
        return obj.death_date is None

    display_alive.short_description = "Alive"
    display_alive.boolean = True


class CriticAdmin(DisplayAliveMixin, admin.ModelAdmin):
    actions = [reset_view_count]
    list_display = (
        "id",
        "name",
        "expertise_area",
        "total_activity",
        "display_alive",
        "view_count",
    )
    search_fields = ("first_name", "last_name", "expertise_area", "nationality", "id")
    list_filter = (
        "expertise_area",
        AliveFilter,
        "nationality",
        ("birth_date", DateRangeFilterBuilder(title="Birth Date")),
        ("death_date", DateRangeFilterBuilder(title="Death Date")),
    )
    ordering = ("expertise_area", "last_name", "first_name", "view_count")
    readonly_fields = readonly_fields

    fieldsets = (
        (None, {"fields": ("first_name", "last_name", "expertise_area")}),
        (
            "Details",
            {"fields": ("birth_date", "death_date", "nationality", "website", "photo")},
        ),
        auto_fieldset,
    )


class AuthorAdmin(DisplayAliveMixin, admin.ModelAdmin):
    actions = [reset_view_count]
    list_display = (
        "id",
        "name",
        "publications_num",
        "awards_num",
        "popularity",
        "display_alive",
        "view_count",
    )
    search_fields = ("first_name", "last_name", "nationality", "id")
    list_filter = (
        "nationality",
        AliveFilter,
        AwardedFilter,
        PublishedFilter,
        PopularityFilter,
        ("birth_date", DateRangeFilterBuilder(title="Birth Date")),
        ("death_date", DateRangeFilterBuilder(title="Death Date")),
    )
    ordering = ("last_name", "first_name", "view_count")
    readonly_fields = readonly_fields

    fieldsets = (
        (None, {"fields": ("first_name", "last_name")}),
        (
            "Details",
            {"fields": ("birth_date", "death_date", "nationality", "website", "photo")},
        ),
        auto_fieldset,
    )


admin.site.register(Critic, CriticAdmin)
admin.site.register(Author, AuthorAdmin)
