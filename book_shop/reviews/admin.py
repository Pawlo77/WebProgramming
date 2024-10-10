from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from utils.admin import auto_fieldset, readonly_fields

from .models import Reaction, Review

User = get_user_model()


@admin.action(description="Star selected reviews")
def star_review(modeladmin, request, queryset):
    for review in queryset:
        review.star_review(request.user)
    modeladmin.message_user(
        request, f"{queryset.count()} review(s) were successfully starred."
    )


@admin.action(description="Unstar selected reviews")
def unstar_review(modeladmin, request, queryset):
    for review in queryset:
        review.unstar_review(request.user)
    modeladmin.message_user(
        request, f"{queryset.count()} review(s) were successfully unstarred."
    )


class ContentTypeFilter(admin.SimpleListFilter):
    title = "Content Type"
    parameter_name = "content_type"

    def lookups(self, request, model_admin):
        return [
            (ContentType.objects.get(app_label="items", model="book").id, "Book"),
            (ContentType.objects.get(app_label="people", model="author").id, "Author"),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type=self.value())
        return queryset


class ReviewAdmin(admin.ModelAdmin):
    actions = [star_review, unstar_review]
    list_display = (
        "id",
        "critic_name",
        "content_type",
        "object_id",
        "starred",
        "like_count",
        "dislike_count",
        "view_count",
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
    ordering = ("content_type", "critic__last_name", "critic__first_name", "view_count")
    readonly_fields = readonly_fields

    fieldsets = (
        (None, {"fields": ("content_type", "object_id", "critic", "starred")}),
        ("Content", {"fields": ("content",)}),
        ("Details", {"fields": ("date_starred", "starred_by")}),
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
        (None, {"fields": ("review", "reaction_type")}),
        auto_fieldset,
    )


admin.site.register(Review, ReviewAdmin)
admin.site.register(Reaction, ReactionAdmin)
