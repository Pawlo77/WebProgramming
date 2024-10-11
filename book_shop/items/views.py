
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from .forms import BookFilterForm
from .models import Award, Book


class AwardDetailView(LoginRequiredMixin, DetailView):
    """View for displaying details of an Award."""

    model = Award
    template_name = "award.html"
    context_object_name = "award"

    def get_object(self):
        """Update view count when the award details are accessed."""
        award = super().get_object()
        award.update_views()
        return award


class BookDetailView(DetailView):
    """View for displaying details of a Book."""

    model = Book
    template_name = "book.html"
    context_object_name = "book"

    def get_object(self):
        """Update view count when the book details are accessed."""
        book = super().get_object()
        book.update_views()
        return book

    def get_context_data(self, **kwargs):
        """Add like and dislike statuses for reviews to the context."""
        context = super().get_context_data(**kwargs)
        context.update(self._get_like_dislike_statuses())
        return context

    def _get_like_dislike_statuses(self):
        """Helper method to retrieve like/dislike statuses for reviews."""
        like_statuses_active = {}
        like_statuses_unactive = {}
        disliked_statuses_active = {}
        disliked_statuses_unactive = {}

        for (
            review
        ) in (
            self.object.reviews.all()
        ):  # Use self.object for the current book's reviews
            user = self.request.user
            has_liked = review.has_liked(user)
            has_disliked = review.has_disliked(user)

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


class BookListView(ListView):
    """View for displaying a list of Books with filtering options."""

    model = Book
    template_name = "books.html"
    context_object_name = "books"
    paginate_by = 10

    def get_queryset(self):
        """Retrieve and filter the queryset of books."""
        queryset = super().get_queryset().order_by("-view_count", "-rating")
        form = BookFilterForm(self.request.GET or None)

        if form.is_valid():
            queryset = self._filter_queryset(queryset, form.cleaned_data)

        return queryset

    def _filter_queryset(self, queryset, cleaned_data):
        """Filter queryset based on cleaned data from the form."""
        title = cleaned_data.get("title")
        author = cleaned_data.get("author")
        date_published = cleaned_data.get("date_published")
        language = cleaned_data.get("language")
        rating = cleaned_data.get("rating")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author=author)
        if date_published:
            queryset = queryset.filter(date_published=date_published)
        if language:
            queryset = queryset.filter(language__icontains=language)
        if rating:
            queryset = queryset.filter(rating=rating)

        return queryset

    def get_context_data(self, **kwargs):
        """Add the filter form to the context."""
        context = super().get_context_data(**kwargs)
        context["form"] = BookFilterForm(self.request.GET or None)
        return context
