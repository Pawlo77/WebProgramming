from django.urls import path

from .views import AuthorDetailView, AuthorListView, CriticDetailView, CriticListView

urlpatterns = [
    path("authors", AuthorListView.as_view(), name="author-list"),
    path("authors/<int:pk>/", AuthorDetailView.as_view(), name="author-detail"),
    path("critics", CriticListView.as_view(), name="critic-list"),
    path("critics/<int:pk>/", CriticDetailView.as_view(), name="critic-detail"),
]
