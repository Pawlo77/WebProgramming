from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from .models import Review


class ReviewActionView(LoginRequiredMixin, View):
    """Base class to handle liking and disliking a review."""

    def get_review(self, review_id):
        """Retrieve the review object or return a 404 error if not found."""
        return get_object_or_404(Review, id=review_id)

    def toggle_like(self, review, user):
        """Toggle the like status for a review."""
        if review.has_liked(user):
            review.delete_like(user)
            return False
        else:
            review.add_like(user)
            return True

    def toggle_dislike(self, review, user):
        """Toggle the dislike status for a review."""
        if review.has_disliked(user):
            review.delete_dislike(user)
            return False
        else:
            review.add_dislike(user)
            return True


class LikeView(ReviewActionView):
    """View for liking a review."""

    def post(self, request, review_id):
        review = self.get_review(review_id)
        disliked = review.has_disliked(request.user)

        if disliked:
            review.delete_dislike(request.user)

        liked = self.toggle_like(review, request.user)

        return JsonResponse(
            {
                "liked": liked,
                "like_count": review.like_count,
                "dislike_count": review.dislike_count,
            }
        )


class DislikeView(ReviewActionView):
    """View for disliking a review."""

    def post(self, request, review_id):
        review = self.get_review(review_id)
        liked = review.has_liked(request.user)

        if liked:
            review.delete_like(request.user)

        disliked = self.toggle_dislike(review, request.user)

        return JsonResponse(
            {
                "disliked": disliked,
                "like_count": review.like_count,
                "dislike_count": review.dislike_count,
            }
        )
