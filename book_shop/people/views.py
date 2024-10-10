from django.db.models import Count, ExpressionWrapper, F, FloatField, Max, Q
from django.views.generic import DetailView, ListView

from .forms import AuthorFilterForm, CriticFilterForm
from .models import Author, Critic


class BaseDetailView(DetailView):
    """Base detail view to handle updating view counts and fetching like/dislike statuses."""

    def get_object(self):
        obj = super().get_object()
        obj.update_views()
        return obj

    def get_like_dislike_statuses(self, reviews):
        """Helper method to get like/dislike statuses for reviews."""
        like_statuses_active = {}
        like_statuses_unactive = {}
        disliked_statuses_active = {}
        disliked_statuses_unactive = {}

        for review in reviews:
            has_liked = review.has_liked(self.request.user)
            has_disliked = review.has_disliked(self.request.user)

            like_statuses_active[review.id] = "" if has_liked else "none"
            like_statuses_unactive[review.id] = "none" if has_liked else ""
            disliked_statuses_active[review.id] = "" if has_disliked else "none"
            disliked_statuses_unactive[review.id] = "none" if has_disliked else ""

        return {
            "like_statuses_active": like_statuses_active,
            "like_statuses_unactive": like_statuses_unactive,
            "disliked_statuses_active": disliked_statuses_active,
            "disliked_statuses_unactive": disliked_statuses_unactive,
        }


class AuthorDetailView(BaseDetailView):
    """View for displaying details of an Author."""

    model = Author
    template_name = "author.html"
    context_object_name = "author"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_like_dislike_statuses(self.object.reviews.all()))
        return context


class AuthorListView(ListView):
    """View for displaying a list of Authors with filtering options."""

    model = Author
    template_name = "authors.html"
    context_object_name = "authors"
    paginate_by = 10

    def get_queryset(self):
        max_views = (
            Author.objects.aggregate(max_views=Max("view_count"))["max_views"] or 1
        )
        queryset = (
            super()
            .get_queryset()
            .annotate(
                publications_count=Count("books"),
                author_popularity=ExpressionWrapper(
                    F("view_count") / max_views * 10,
                    output_field=FloatField(),
                ),
            )
            .order_by("-publications_count", "-author_popularity")
        )

        form = AuthorFilterForm(self.request.GET or None)
        if form.is_valid():
            queryset = self._apply_filters(queryset, form.cleaned_data)

        return queryset

    def _apply_filters(self, queryset, cleaned_data):
        """Apply filters to the queryset based on the cleaned data."""
        if cleaned_data.get("name"):
            queryset = queryset.filter(
                Q(first_name__icontains=cleaned_data["name"])
                | Q(last_name__icontains=cleaned_data["name"])
            )
        if cleaned_data.get("nationality"):
            queryset = queryset.filter(nationality=cleaned_data["nationality"])
        if cleaned_data.get("birth_year"):
            queryset = queryset.filter(birth_date__year=cleaned_data["birth_year"])
        if cleaned_data.get("website"):
            queryset = queryset.filter(website__icontains=cleaned_data["website"])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AuthorFilterForm(self.request.GET or None)
        return context


class CriticDetailView(BaseDetailView):
    """View for displaying details of a Critic."""

    model = Critic
    template_name = "critic.html"
    context_object_name = "critic"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_like_dislike_statuses(self.object.reviews.all()))
        return context


class CriticListView(ListView):
    """View for displaying a list of Critics with filtering options."""

    model = Critic
    template_name = "critics.html"
    context_object_name = "critics"
    paginate_by = 10

    def get_queryset(self):
        max_views = (
            Critic.objects.aggregate(max_views=Max("view_count"))["max_views"] or 1
        )
        queryset = (
            super()
            .get_queryset()
            .annotate(
                publications_count=Count("reviews"),
                critic_popularity=ExpressionWrapper(
                    F("view_count") / max_views * 10,
                    output_field=FloatField(),
                ),
            )
            .order_by("-publications_count", "-critic_popularity")
        )

        form = CriticFilterForm(self.request.GET or None)
        if form.is_valid():
            queryset = self._apply_filters(queryset, form.cleaned_data)

        return queryset

    def _apply_filters(self, queryset, cleaned_data):
        """Apply filters to the queryset based on the cleaned data."""
        if cleaned_data.get("name"):
            queryset = queryset.filter(
                Q(first_name__icontains=cleaned_data["name"])
                | Q(last_name__icontains=cleaned_data["name"])
            )
        if cleaned_data.get("nationality"):
            queryset = queryset.filter(nationality=cleaned_data["nationality"])
        if cleaned_data.get("birth_year"):
            queryset = queryset.filter(birth_date__year=cleaned_data["birth_year"])
        if cleaned_data.get("website"):
            queryset = queryset.filter(website__icontains=cleaned_data["website"])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CriticFilterForm(self.request.GET or None)
        return context
