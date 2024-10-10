from django.db.models import Count, ExpressionWrapper, F, FloatField, Max, Q
from django.views.generic import DetailView, ListView

from .forms import AuthorFilterForm, CriticFilterForm
from .models import Author, Critic


class AuthorDetailView(DetailView):
    model = Author
    template_name = "author.html"
    context_object_name = "author"

    def get_object(self):
        author = super().get_object()
        author.update_views()
        return author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        like_statuses_active = {}
        like_statuses_unactive = {}
        disliked_statuses_active = {}
        disliked_statuses_unactive = {}
        for author in self.get_queryset().all():
            for review in author.reviews:
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


class AuthorListView(ListView):
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
            name = form.cleaned_data.get("name")
            nationality = form.cleaned_data.get("nationality")
            birth_year = form.cleaned_data.get("birth_year")
            website = form.cleaned_data.get("website")

            if name:
                queryset = queryset.filter(
                    Q(first_name__icontains=name) | Q(last_name__icontains=name)
                )
            if nationality:
                queryset = queryset.filter(nationality=nationality)
            if birth_year:
                queryset = queryset.filter(birth_date__year=birth_year)
            if website:
                queryset = queryset.filter(website__icontains=website)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = AuthorFilterForm(self.request.GET or None)
        return context


class CriticDetailView(DetailView):
    model = Critic
    template_name = "critic.html"
    context_object_name = "critic"

    def get_object(self):
        critic = super().get_object()
        critic.update_views()
        return critic

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        like_statuses_active = {}
        like_statuses_unactive = {}
        disliked_statuses_active = {}
        disliked_statuses_unactive = {}
        for critic in self.get_queryset().all():
            for review in critic.reviews.all():
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


class CriticListView(ListView):
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
                author_popularity=ExpressionWrapper(
                    F("view_count") / max_views * 10,
                    output_field=FloatField(),
                ),
            )
            .order_by("-publications_count", "-author_popularity")
        )

        form = CriticFilterForm(self.request.GET or None)

        if form.is_valid():
            name = form.cleaned_data.get("name")
            nationality = form.cleaned_data.get("nationality")
            birth_year = form.cleaned_data.get("birth_year")
            website = form.cleaned_data.get("website")

            if name:
                queryset = queryset.filter(
                    Q(first_name__icontains=name) | Q(last_name__icontains=name)
                )
            if nationality:
                queryset = queryset.filter(nationality=nationality)
            if birth_year:
                queryset = queryset.filter(birth_date__year=birth_year)
            if website:
                queryset = queryset.filter(website__icontains=website)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CriticFilterForm(self.request.GET or None)
        return context
