from datetime import date

from django.db import models
from django.db.models import Count, Max, Min
from users.models import CustomUser
from utils.models import Item


class Person(Item):
    """Common fields for Author and Critic."""

    # Basic information
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(
        help_text="Brief biography or description.", null=True, blank=True
    )
    birth_date = models.DateField(help_text="Birth date.", null=False, blank=False)
    death_date = models.DateField(
        null=True, blank=True, help_text="Death date, if applicable."
    )
    nationality = models.CharField(
        max_length=100,
        help_text="Nationality or country of origin.",
        null=True,
        blank=True,
    )

    # Photo and Website
    website = models.URLField(
        blank=True, null=True, help_text="Author's official website or portfolio link."
    )
    photo = models.ImageField(
        upload_to="author_photos/",
        blank=True,
        null=True,
        help_text="Author's photograph.",
    )

    class Meta:
        unique_together = ("last_name", "first_name")
        ordering = ["last_name", "first_name"]
        verbose_name_plural = "People"
        abstract = True
        indexes = [
            models.Index(fields=["birth_date"]),
            models.Index(fields=["death_date"]),
            models.Index(fields=["view_count"]),
            models.Index(fields=["date_updated"]),
        ]

    @property
    def age(self):
        if self.birth_date:
            return (date.today() - self.birth_date).days // 365
        return None

    @property
    def name(self):
        """Joins author names"""
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"Person {self.first_name} {self.last_name}"


class Author(Person):
    # Auto-generated fields
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="author_created_by",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="author_updated_by",
    )

    class Meta:
        verbose_name_plural = "Authors"

    @property
    def first_publication_date(self):
        """Calculates min publication_date among author's books"""
        return self.books.aggregate(min_date_published=Min("date_published"))[
            "min_date_published"
        ]

    @property
    def last_publication_date(self):
        """Calculates max publication_date among author's books"""
        return self.books.aggregate(max_date_published=Max("date_published"))[
            "max_date_published"
        ]

    @property
    def career_span(self):
        """Calculates the number of years between first and last publication."""
        if self.first_publication_date and self.last_publication_date:
            return (
                self.last_publication_date - self.first_publication_date
            ).days // 365
        return None

    @property
    def publications_num(self):
        """Number of Author's publications."""
        return self.books.count()

    @property
    def best_rated_book(self):
        """Get the book with the best (highest) rating."""
        return self.books.order_by("-rating").first()

    @property
    def mostly_reviewed_book(self):
        """Get the book with the most reviews written."""
        return (
            self.books.annotate(review_count=Count("reviews"))
            .order_by("-review_count")
            .first()
        )

    @property
    def awards_num(self):
        """Number of Author's awards."""
        return self.awards.count()

    @property
    def first_award_date(self):
        """Number of Author's awards."""
        return self.awards.aggregate(min_year_awarded=Min("year_awarded"))[
            "min_year_awarded"
        ]

    @property
    def last_award_date(self):
        """Number of Author's awards."""
        return self.awards.aggregate(max_year_awarded=Max("year_awarded"))[
            "max_year_awarded"
        ]

    @property
    def popularity(self):
        """
        Calculates the popularity based on view_count.
        The maximum popularity score is 10, based on the highest view_count among all persons.
        """
        max_views = (
            Author.objects.aggregate(max_views=models.Max("view_count"))["max_views"]
            or 1
        )  # Avoid division by zero
        if self.view_count > max_views:
            return 10  # Maximum popularity
        else:
            return (self.view_count / max_views) * 10  # Scale popularity

    def __str__(self):
        return f"Author {self.first_name} {self.last_name}"


class Critic(Person):
    expertise_area = models.CharField(
        max_length=255, help_text="Critic's area of expertise.", null=False, blank=False
    )

    # Auto-generated fields
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="critic_created_by",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="critic_updated_by",
    )

    class Meta:
        verbose_name_plural = "Critics"

    @property
    def total_activity(self):
        """Calculates the number of reviews / coments given by a Criti."""
        return self.reviews.count()

    @property
    def date_first_review(self):
        """Calculates the date of first critic's review."""
        return self.reviews.aggregate(min_date_created=Min("date_created"))[
            "min_date_created"
        ]

    @property
    def date_last_review(self):
        """Calculates the date of last critic's review"""
        return self.reviews.aggregate(max_date_created=Max("date_created"))[
            "max_date_created"
        ]

    def __str__(self):
        return f"Critic {self.first_name} {self.last_name}"
