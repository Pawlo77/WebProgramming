from django.urls import path

from .views import AwardDetailView, BookDetailView, BookListView

urlpatterns = [
    path("books", BookListView.as_view(), name="book-list"),
    path("books/<int:pk>/", BookDetailView.as_view(), name="book-detail"),
    path("awards/<int:pk>/", AwardDetailView.as_view(), name="award-detail"),
]
