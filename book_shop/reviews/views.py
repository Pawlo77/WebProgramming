from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View

from .models import Review


class LikeView(LoginRequiredMixin, View):
    def post(self, request, review_id):
        review = Review.objects.get(id=review_id)

        if review.has_disliked(request.user):
            review.delete_dislike(request.user)

        if review.has_liked(request.user):
            review.delete_like(request.user)
            liked = False
        else:
            review.add_like(request.user)
            liked = True

        return JsonResponse(
            {
                "liked": liked,
                "like_count": review.like_count,
                "dislike_count": review.dislike_count,
            }
        )


class DislikeView(LoginRequiredMixin, View):
    def post(self, request, review_id):
        review = Review.objects.get(id=review_id)

        if review.has_liked(request.user):
            review.delete_like(request.user)

        if review.has_disliked(request.user):
            review.delete_dislike(request.user)
            disliked = False
        else:
            review.add_dislike(request.user)
            disliked = True

        return JsonResponse(
            {
                "disliked": disliked,
                "like_count": review.like_count,
                "dislike_count": review.dislike_count,
            }
        )
