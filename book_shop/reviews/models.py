from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models
from django.urls import reverse
from django.utils import timezone
from people.models import Author, Critic
from users.models import CustomUser
from utils.models import Item


class Review(Item):
    """Critic review of the author or a book."""

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Model type being reviewed (author or book).",
    )
    object_id = models.PositiveIntegerField(
        help_text="The ID of the object being reviewed (author or book)."
    )
    content_object = GenericForeignKey("content_type", "object_id")

    content = models.TextField(
        help_text="The comment or review content.", null=False, blank=False
    )

    critic = models.ForeignKey(
        Critic,
        on_delete=models.CASCADE,
        related_name="reviews",
        help_text="The critic writing the review.",
    )

    starred = models.BooleanField(
        help_text="Indicates whether the review is pinned at the top.", default=False
    )
    date_starred = models.DateTimeField(
        null=True, blank=True, help_text="Date the review was starred."
    )
    starred_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="starred_by",
        help_text="User who starred the review.",
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
        """Return the number of likes for the review."""
        return self.reactions.filter(reaction_type=Reaction.ReactionType.LIKE).count()

    @property
    def dislike_count(self):
        """Return the number of dislikes for the review."""
        return self.reactions.filter(
            reaction_type=Reaction.ReactionType.DISLIKE
        ).count()

    @property
    def net_likes(self):
        """Return net likes (likes - dislikes) for the review."""
        return self.like_count - self.dislike_count

    @property
    def review_object(self):
        """Returns review's object"""
        from items.models import Book

        if self.content_type == ContentType.objects.get_for_model(Book):
            book = Book.objects.filter(id=self.object_id).first()
            book.url = reverse("book-detail", args=[book.pk])
            return book
        author = Author.objects.filter(id=self.object_id).first()
        author.url = reverse("author-detail", args=[author.pk])
        return author

    def add_like(self, user):
        """Add a like reaction to the review by a user."""
        Reaction.objects.create(
            created_by=user,
            reaction_type=Reaction.ReactionType.LIKE,
            review=self,
            updated_by=user,
        )

    def add_dislike(self, user):
        """Add a dislike reaction to the review by a user."""
        Reaction.objects.create(
            created_by=user,
            reaction_type=Reaction.ReactionType.DISLIKE,
            review=self,
            updated_by=user,
        )

    def delete_like(self, user):
        """Remove a like reaction from the review by a user."""
        self.reactions.filter(
            reaction_type=Reaction.ReactionType.LIKE, created_by=user
        ).delete()

    def delete_dislike(self, user):
        """Remove a dislike reaction from the review by a user."""
        self.reactions.filter(
            reaction_type=Reaction.ReactionType.DISLIKE, created_by=user
        ).delete()

    def has_liked(self, user):
        """Check if the user has liked the review."""
        return (
            user.is_authenticated
            and self.reactions.filter(
                created_by=user, reaction_type=Reaction.ReactionType.LIKE
            ).exists()
        )

    def has_disliked(self, user):
        """Check if the user has disliked the review."""
        return (
            user.is_authenticated
            and self.reactions.filter(
                created_by=user, reaction_type=Reaction.ReactionType.DISLIKE
            ).exists()
        )

    def star_review(self, user):
        """Star the review, restricted to users with the Manager or Admin role."""
        if user.role not in [CustomUser.MANAGER, CustomUser.ADMIN]:
            raise PermissionDenied(
                "Only users with Manager or Admin roles can star a review."
            )
        self.starred = True
        self.date_starred = timezone.now()
        self.starred_by = user
        self.save()

    def unstar_review(self, user):
        """Unstar the review, restricted to users with the Manager or Admin role."""
        if user.role not in [CustomUser.MANAGER, CustomUser.ADMIN]:
            raise PermissionDenied(
                "Only users with Manager or Admin roles can unstar a review."
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
        help_text="Reaction type: Like or Dislike.",
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
        unique_together = ("created_by", "review")
        indexes = [
            models.Index(fields=["review", "reaction_type"]),
        ]

    def __str__(self):
        return f"{self.created_by.username} - {self.reaction_type} on {self.review}"
