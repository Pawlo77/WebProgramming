from datetime import date

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils import timezone
from people.models import Critic
from users.models import CustomUser
from utils.models import Item


class Review(Item):
    """Critic review of the author or a book."""

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=False, blank=False
    )
    object_id = models.PositiveIntegerField(null=False, blank=False)
    content_object = GenericForeignKey("content_type", "object_id")

    content = models.TextField(
        help_text="The comment or review.", null=False, blank=False
    )

    critic = models.ForeignKey(
        Critic,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=False,
        blank=False,
    )

    starred = models.BooleanField(
        help_text="Star review to pin it to top.",
        default=False,
        blank=False,
        null=False,
    )
    date_starred = models.DateTimeField(
        null=True, blank=True, help_text="Date when the review was starred."
    )
    starred_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="starred_by",
    )

    # Auto-generated fields
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="review_created_by",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="review_updated_by",
    )

    class Meta:
        unique_together = ("content_type", "object_id", "critic")
        verbose_name_plural = "Reviews"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["date_updated"]),
        ]

    @property
    def like_count(self):
        """Calculate the number of likes for the comment."""
        return self.reactions.filter(reaction_type=Reaction.ReactionType.LIKE).count()

    @property
    def dislike_count(self):
        """Calculate the number of dislikes for the comment."""
        return self.reactions.filter(
            reaction_type=Reaction.ReactionType.DISLIKE
        ).count()

    @property
    def net_likes(self):
        """Calculate the net likes (likes - dislikes) for the comment."""
        return self.like_count - self.dislike_count

    def add_like(self, user):
        """Adds user like to current review."""
        Reaction.objects.create(
            created_by=user,
            reaction_type=Reaction.ReactionType.LIKE,
            review=self,
            updated_by=user,
        )

    def add_dislike(self, user):
        """Adds user dislike to current review."""
        Reaction.objects.create(
            created_by=user,
            reaction_type=Reaction.ReactionType.DISLIKE,
            review=self,
            updated_by=user,
        )

    def delete_like(self, user):
        """Remove user like to current review."""
        Reaction.objects.filter(
            reaction_type=Reaction.ReactionType.LIKE, created_by=user
        ).delete()

    def delete_dislike(self, user):
        """Remove user dislike to current review."""
        Reaction.objects.filter(
            reaction_type=Reaction.ReactionType.DISLIKE, created_by=user
        ).delete()

    def has_liked(self, user):
        """Check if given user has liked this review."""
        if user.is_authenticated:
            return self.reactions.filter(
                created_by=user, reaction_type=Reaction.ReactionType.LIKE
            ).exists()
        return False

    def has_disliked(self, user):
        """Check if given user has disliked this review."""
        if user.is_authenticated:
            return self.reactions.filter(
                created_by=user, reaction_type=Reaction.ReactionType.DISLIKE
            ).exists()
        return False

    def star_review(self, user):
        """
        Method to star a review.
        Only users with the 'Manager' or 'Admin' role can star the review.
        """
        if user.role not in [CustomUser.MANAGER, CustomUser.ADMIN]:
            raise PermissionDenied(
                "Only users with Manager or Admin roles can star a review."
            )

        # Star the review
        self.starred = True
        self.date_starred = timezone.now()
        self.starred_by = user
        self.save()

    def unstar_review(self, user):
        """
        Method to unstar a review.
        Only users with the 'Manager' or 'Admin' role can unstar the review.
        Clears the 'starred', 'starred_by', and 'date_starred' fields.
        """
        if user.role not in [CustomUser.MANAGER, CustomUser.ADMIN]:
            raise PermissionDenied(
                "Only users with Manager or Admin roles can star a review."
            )
        self.starred = False
        self.date_starred = None
        self.starred_by = None
        self.save()

    def __str__(self):
        return f"Review by {self.critic.name} on {self.content_object}"


class Reaction(Item):
    """Reaction model to track likes or dislikes for reviews."""

    class ReactionType(models.TextChoices):
        LIKE = "like", "Like"
        DISLIKE = "dislike", "Dislike"

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="reactions"
    )
    reaction_type = models.CharField(
        max_length=10,
        choices=ReactionType.choices,
        help_text="Reaction type: Like or Dislike",
    )

    # Auto-generated fields
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reaction_created_by",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reaction_updated_by",
    )

    class Meta:
        unique_together = (
            "created_by",
            "review",
        )

    def __str__(self):
        return f"{self.created_by.username} - {self.reaction_type} on {self.review}"
