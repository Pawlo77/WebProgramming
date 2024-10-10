from django.db.models import Q
from django.views.generic import DetailView, ListView

from .forms import AuthoFilterForm
from .models import Author


class AuthorDetailView(DetailView):
    model = Author
    template_name = "author.html"
    context_object_name = "author"

    def get_object(self):
        author = super().get_object()
        author.update_views()
        return author


class AuthorListView(ListView):
    model = Author
    template_name = "authors.html"
    context_object_name = "authors"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        form = AuthoFilterForm(self.request.GET or None)

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
        context["form"] = AuthoFilterForm(self.request.GET or None)
        return context
