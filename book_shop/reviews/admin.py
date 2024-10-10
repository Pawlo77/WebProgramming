from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from utils.admin import auto_fieldset, readonly_fields

from .models import Reaction, Review


class ContentTypeFilter(admin.SimpleListFilter):
    title = "Content Type"
    parameter_name = "content_type"

    def lookups(self, request, model_admin):
        return [
            (
                ContentType.objects.get(app_label="items", model="book").id,
                "Book",
            ),
            (
                ContentType.objects.get(app_label="people", model="author").id,
                "Author",
            ),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type=self.value())
        return queryset


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "critic_name",
        "content_type",
        "object_id",
        "starred",
        "like_count",
        "dislike_count",
    )
    search_fields = ("critic__first_name", "critic__last_name", "id", "object_id")
    list_filter = (
        ContentTypeFilter,
        "critic__first_name",
        "critic__last_name",
        "starred",
        "starred_by__first_name",
        "starred_by__last_name",
        "object_id",
    )
    ordering = ("content_type", "critic__last_name", "critic__first_name")
    readonly_fields = readonly_fields

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "content_type",
                    "object_id",
                    "critic",
                    "starred",
                )
            },
        ),
        (
            "content",
            {"fields": ("content",)},
        ),
        (
            "details",
            {"fields": ("date_starred", "starred_by")},
        ),
        auto_fieldset,
    )

    def critic_name(self, obj):
        return obj.critic.name

    critic_name.short_description = "Critic"


class ReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "review__id", "review__content_type", "reaction_type")
    search_fields = (
        "review__id",
        "created_by__last_name",
        "created_by__first_name",
        "id",
    )
    list_filter = (
        "review__id",
        "created_by__last_name",
        "created_by__first_name",
        "reaction_type",
    )
    ordering = (
        "reaction_type",
        "review__id",
        "created_by__last_name",
        "created_by__first_name",
    )
    readonly_fields = readonly_fields

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "review",
                    "reaction_type",
                )
            },
        ),
        auto_fieldset,
    )

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff or request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_staff or request.user.is_superuser


admin.site.register(Review, ReviewAdmin)
admin.site.register(Reaction, ReactionAdmin)
