from django.urls import path

from .views import AuthorDetailView, AuthorListView

urlpatterns = [
    path("authors", AuthorListView.as_view(), name="author-list"),
    path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author-detail"),
]
