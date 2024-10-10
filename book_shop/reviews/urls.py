from django.urls import path

from .views import DislikeView, LikeView

urlpatterns = [
    path("<int:review_id>/like/", LikeView.as_view(), name="like_review"),
    path("<int:review_id>/dislike/", DislikeView.as_view(), name="dislike_review"),
]
