from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Case, Count, F, IntegerField, When
from people.models import Author
from reviews.models import Reaction, Review
from users.models import CustomUser
from utils.models import Item


class Award(Item):
    """
    Model representing an award given to an author.

    This model tracks basic information about the award, the recipient author,
    and metadata such as view count and user actions.
    """

    # Basic information about the award
    name = models.CharField(max_length=255, help_text="Name of the award.")
    description = models.TextField(
        blank=True, null=True, help_text="Description or significance of the award."
    )
    year_awarded = models.IntegerField(
        help_text="Year the award was received.",
        default=date.today().year,
        validators=[MinValueValidator(1900), MaxValueValidator(date.today().year)],
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="awards",
        help_text="Author who received the award.",
    )

    # Optional links and images
    website = models.URLField(
        blank=True, null=True, help_text="Link to the official website of the award."
    )
    photo = models.ImageField(
        upload_to="award_photos/",
        blank=True,
        null=True,
        help_text="Photograph or logo of the award.",
    )

    # Tracking views and user-related actions
    view_count = models.PositiveIntegerField(
        default=0, help_text="Number of times this award entry has been viewed."
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="award_created_by",
        help_text="User who created this award entry.",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="award_updated_by",
        help_text="User who last updated this award entry.",
    )

    class Meta:
        unique_together = ("name", "year_awarded", "author")
        verbose_name_plural = "Awards"
        ordering = ["-year_awarded"]
        indexes = [
            models.Index(fields=["year_awarded"]),
            models.Index(fields=["author"]),
            models.Index(fields=["date_updated"]),
        ]

    def __str__(self):
        return f"Award {self.name} ({self.year_awarded}) for {self.author.name}"

    @property
    def age(self):
        """Calculate the number of years since the award was received."""
        current_year = date.today().year
        return current_year - self.year_awarded if self.year_awarded else None


class Book(Item):
    """
    Model representing a book written by an author.

    This model contains metadata about the book, such as title, author, publication details,
    and user interactions like ratings and reviews.
    """

    # Core book information
    title = models.CharField(max_length=200, help_text="Title of the book.")
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="books",
        help_text="Author of the book.",
    )
    cover_image = models.ImageField(
        upload_to="covers/", blank=True, null=True, help_text="Cover image of the book."
    )
    summary = models.TextField(
        blank=True, null=True, help_text="Brief summary of the book."
    )

    # Book's technical details
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rating of the book (from 0 to 5).",
    )
    pages = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total number of pages in the book.",
    )
    language = models.CharField(
        max_length=30, help_text="Language the book is written in."
    )
    isbn = models.CharField(
        max_length=13, unique=True, help_text="Unique ISBN number for the book."
    )
    date_published = models.DateField(help_text="Date the book was published.")

    # Tracking fields for user actions
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="book_created_by",
        help_text="User who created this book entry.",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="book_updated_by",
        help_text="User who last updated this book entry.",
    )

    class Meta:
        unique_together = ("title", "author")
        verbose_name_plural = "Books"
        ordering = ["-date_published"]
        indexes = [
            models.Index(fields=["author"]),
            models.Index(fields=["date_published"]),
            models.Index(fields=["language"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["date_updated"]),
        ]

    def __str__(self):
        return f'"{self.title}" by {self.author.name}'

    @property
    def age(self):
        """Calculate the age of the book based on the publication date."""
        if self.date_published:
            return date.today().year - self.date_published.year
        return None

    @property
    def review_num(self):
        """Return the total number of reviews for this book."""
        book_ct = ContentType.objects.get_for_model(Book)
        return Review.objects.filter(content_type=book_ct, object_id=self.id).count()

    @property
    def reviews(self):
        """
        Get all reviews associated with this book, annotated with like and dislike counts.

        Reviews are ordered by starred status and net likes (likes minus dislikes).
        """
        book_ct = ContentType.objects.get_for_model(Book)
        return (
            Review.objects.filter(content_type=book_ct, object_id=self.id)
            .annotate(
                query_likes_count=Count(
                    Case(
                        When(
                            reactions__reaction_type=Reaction.ReactionType.LIKE, then=1
                        ),
                        output_field=IntegerField(),
                    )
                ),
                query_dislikes_count=Count(
                    Case(
                        When(
                            reactions__reaction_type=Reaction.ReactionType.DISLIKE,
                            then=1,
                        ),
                        output_field=IntegerField(),
                    )
                ),
                query_net_likes=F("query_likes_count") - F("query_dislikes_count"),
            )
            .order_by("-starred", "-query_likes_count", "-query_net_likes")
        )
