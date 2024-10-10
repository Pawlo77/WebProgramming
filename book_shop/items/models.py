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
    """Model representing an award given to an author."""

    # Basic information about the award
    name = models.CharField(
        max_length=255,
        help_text="Name of the award.",
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description or significance of the award.",
    )
    year_awarded = models.IntegerField(
        help_text="Year the award was received.",
        null=False,
        blank=True,
        default=date.today().year,
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="awards",
        help_text="Author who received the award.",
    )

    # Additional information about the award
    website = models.URLField(
        blank=True,
        null=True,
        help_text="Award's official website link.",
    )
    photo = models.ImageField(
        upload_to="award_photos/",
        blank=True,
        null=True,
        help_text="Award's photograph.",
    )

    # View count for the award
    view_count = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=False,
        help_text="Number of times the award has been viewed on the website.",
    )

    # Auto-generated fields for tracking
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="award_created_by",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="award_updated_by",
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
        return f"{self.name} ({self.year_awarded}) - {self.author}"

    @property
    def age(self):
        """
        Calculates the age of the award from the year it was awarded.
        Returns the age in years.
        """
        if self.year_awarded:
            current_year = date.today().year
            return current_year - self.year_awarded
        return None


class Book(Item):
    """Model representing a book."""

    # Basic information about the book
    title = models.CharField(max_length=200, null=False, blank=False)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="books",
    )
    cover_image = models.ImageField(upload_to="covers/", blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=False,
        blank=True,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )

    # Technical information about the book
    pages = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=30, null=False, blank=False)
    isbn = models.CharField(max_length=13, unique=True, null=False, blank=False)
    date_published = models.DateField(null=False, blank=False)

    # Auto-generated fields for tracking
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="book_created_by",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="book_updated_by",
    )

    class Meta:
        unique_together = ("title", "author")
        verbose_name_plural = "Books"
        indexes = [
            models.Index(fields=["author"]),
            models.Index(fields=["date_published"]),
            models.Index(fields=["language"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["date_updated"]),
        ]

    @property
    def age(self):
        """Calculate the age of the book based on the published date."""
        if self.date_published:
            return date.today().year - self.date_published.year
        return None

    @property
    def review_num(self):
        """Calculate the number of reviews for the book."""
        book_ct = ContentType.objects.get_for_model(Book)
        return Review.objects.filter(content_type=book_ct, object_id=self.id).count()

    @property
    def reviews(self):
        """Get reviews for the book, including likes and dislikes."""
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
            .order_by("-starred", "-query_net_likes")
        )

    def __str__(self):
        return f"{self.title} by {self.author.name}"
