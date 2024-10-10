import json

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from reviews.models import Reaction, Review

from .forms import BookFilterForm
from .models import Award, Book


class AwardDetailView(DetailView):
    """View for displaying details of an Award."""

    model = Award
    template_name = "award.html"
    context_object_name = "award"

    def get_object(self):
        # Update view count when the award details are accessed
        award = super().get_object()
        award.update_views()
        return award


class BookDetailView(DetailView):
    """View for displaying details of a Book."""

    model = Book
    template_name = "book.html"
    context_object_name = "book"

    def get_object(self):
        # Update view count when the book details are accessed
        book = super().get_object()
        book.update_views()
        return book

    def get_context_data(self, **kwargs):
        """Add like and dislike statuses for reviews to the context."""
        context = super().get_context_data(**kwargs)

        # Dictionaries to hold the like/dislike status for each review
        like_statuses_active = {}
        like_statuses_unactive = {}
        disliked_statuses_active = {}
        disliked_statuses_unactive = {}

        # Iterate through reviews of the book
        for book in self.get_queryset().all():
            for review in book.reviews:
                has_liked = review.has_liked(self.request.user)
                has_disliked = review.has_disliked(self.request.user)

                # Set like/dislike statuses based on user interactions
                like_statuses_active[review.id] = "" if has_liked else "none"
                like_statuses_unactive[review.id] = "none" if has_liked else ""
                disliked_statuses_active[review.id] = "" if has_disliked else "none"
                disliked_statuses_unactive[review.id] = "none" if has_disliked else ""

        # Add the like/dislike status dictionaries to the context
        context["like_statuses_active"] = like_statuses_active
        context["like_statuses_unactive"] = like_statuses_unactive
        context["disliked_statuses_active"] = disliked_statuses_active
        context["disliked_statuses_unactive"] = disliked_statuses_unactive

        return context


class BookListView(ListView):
    """View for displaying a list of Books with filtering options."""

    model = Book
    template_name = "books.html"
    context_object_name = "books"
    paginate_by = 10

    def get_queryset(self):
        # Retrieve and order the queryset of books
        queryset = super().get_queryset().order_by("-view_count", "-rating")
        form = BookFilterForm(self.request.GET or None)

        # Filter queryset based on form data if the form is valid
        if form.is_valid():
            title = form.cleaned_data.get("title")
            author = form.cleaned_data.get("author")
            date_published = form.cleaned_data.get("date_published")
            language = form.cleaned_data.get("language")
            rating = form.cleaned_data.get("rating")

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
