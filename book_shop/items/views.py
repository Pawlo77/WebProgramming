import json

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from .forms import BookFilterForm
from .models import Book, Reaction, Review  # Ensure you import your models


class BookDetailView(DetailView):
    model = Book
    template_name = "book.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        like_statuses_active = {}
        like_statuses_unactive = {}
        disliked_statuses_active = {}
        disliked_statuses_unactive = {}
        for book in self.get_queryset().all():
            for review in book.reviews:
                has_liked = review.has_liked(self.request.user)
                has_disliked = review.has_disliked(self.request.user)

                like_statuses_active[review.id] = "" if has_liked else "none"
                like_statuses_unactive[review.id] = "none" if has_liked else ""
                disliked_statuses_active[review.id] = "" if has_disliked else "none"
                disliked_statuses_unactive[review.id] = "none" if has_disliked else ""

        context["like_statuses_active"] = like_statuses_active
        context["like_statuses_unactive"] = like_statuses_unactive
        context["disliked_statuses_active"] = disliked_statuses_active
        context["disliked_statuses_unactive"] = disliked_statuses_unactive
        return context


class BookListView(ListView):
    model = Book
    template_name = "books.html"
    context_object_name = "books"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = BookFilterForm(self.request.GET or None)

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
        context = super().get_context_data(**kwargs)
        context["form"] = BookFilterForm(self.request.GET or None)
        return context
