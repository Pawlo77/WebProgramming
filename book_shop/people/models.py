from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Case, Count, F, IntegerField, Max, Min, Q, When
from users.models import CustomUser
from utils.models import Item


class Person(Item):
    """
    Abstract model representing a common structure for Authors and Critics.

    This model contains fields and methods that are shared between the Author and Critic models,
    such as basic personal information, profile images, and age-related properties.
    """

    # Basic personal details
    first_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text="First name of the person (required).",
    )
    last_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        help_text="Last name of the person (required).",
    )
    description = models.TextField(
        help_text="Brief biography or description of the person.", null=True, blank=True
    )
    birth_date = models.DateField(
        help_text="Birth date of the person (required).", null=False, blank=False
    )
    death_date = models.DateField(
        help_text="Death date, if applicable.", null=True, blank=True
    )
    nationality = models.CharField(
        max_length=100,
        help_text="Nationality or country of origin of the person.",
        null=True,
        blank=True,
    )

    # Photo and Website
    website = models.URLField(
        help_text="Official website or portfolio link.", blank=True, null=True
    )
    photo = models.ImageField(
        upload_to="person_photos/",
        help_text="Photograph of the person.",
        blank=True,
        null=True,
    )

    # Meta options for the model
    class Meta:
        # Ensure that the combination of first and last name is unique
        unique_together = ("last_name", "first_name")
        ordering = [
            "last_name",
            "first_name",
        ]  # Default ordering by last and first name
        verbose_name_plural = "People"  # Plural name for model admin display
        abstract = True  # Abstract base class to be inherited by other models
        indexes = [
            models.Index(fields=["birth_date"]),
            models.Index(fields=["death_date"]),
            models.Index(fields=["view_count"]),
            models.Index(fields=["date_updated"]),
        ]

    @property
    def age(self):
        """
        Calculates the age of the person based on their birth date and the current date.
        If the birth date is not provided, it returns None.
        """
        if self.birth_date:
            return (date.today() - self.birth_date).days // 365
        return None

    @property
    def name(self):
        """
        Returns the full name by concatenating the first and last names.
        """
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"Person {self.first_name} {self.last_name}"


class Author(Person):
    """
    Model representing an Author, inheriting common fields from the Person model.
    This model includes additional properties such as publications, awards, and career details.
    """

    # Fields for tracking author creation and updates
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="author_created_by",
        help_text="User who created this author entry.",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="author_updated_by",
        help_text="User who last updated this author entry.",
    )

    class Meta:
        verbose_name_plural = "Authors"

    # Properties related to Author's books and publications
    @property
    def first_publication_date(self):
        """
        Returns the earliest publication date of the author's books.
        """
        return self.books.aggregate(min_date_published=Min("date_published"))[
            "min_date_published"
        ]

    @property
    def last_publication_date(self):
        """
        Returns the most recent publication date of the author's books.
        """
        return self.books.aggregate(max_date_published=Max("date_published"))[
            "max_date_published"
        ]

    @property
    def career_span(self):
        """
        Calculates the author's career span in years, based on the first and last publication dates.
        """
        if self.first_publication_date and self.last_publication_date:
            return (
                self.last_publication_date - self.first_publication_date
            ).days // 365
        return None

    @property
    def publications_num(self):
        """
        Returns the total number of books published by the author.
        """
        return self.books.count()

    @property
    def mostly_viewed_book(self):
        """
        Returns the author's book with the most views.
        """
        return self.books.order_by("-view_count").first()

    @property
    def best_rated_book(self):
        """
        Returns the author's book with the highest rating.
        """
        return self.books.order_by("-rating").first()

    @property
    def mostly_reviewed_book(self):
        """
        Returns the author's book with the highest number of reviews.
        """
        return max(self.books.all(), key=lambda book: book.review_num, default=None)

    @property
    def awards_num(self):
        """
        Returns the total number of awards received by the author.
        """
        return self.awards.count()

    @property
    def first_award_date(self):
        """
        Returns the date of the author's first award.
        """
        return self.awards.aggregate(min_year_awarded=Min("year_awarded"))[
            "min_year_awarded"
        ]

    @property
    def last_award_date(self):
        """
        Returns the date of the author's most recent award.
        """
        return self.awards.aggregate(max_year_awarded=Max("year_awarded"))[
            "max_year_awarded"
        ]

    @property
    def popularity(self):
        """
        Calculates the author's popularity as a score from 0 to 10 based on their view count.
        The score is scaled based on the highest view count among all authors.
        """
        max_views = (
            Author.objects.aggregate(max_views=Max("view_count"))["max_views"] or 1
        )
        return min((self.view_count / max_views) * 10, 10)

    @property
    def reviews(self):
        """
        Returns all reviews related to this author, annotated with like and dislike counts.
        Reviews are sorted by 'starred' status and net likes (likes minus dislikes).
        """
        from reviews.models import Reaction, Review

        author_ct = ContentType.objects.get_for_model(Author)

        return (
            Review.objects.filter(content_type=author_ct, object_id=self.id)
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
        return f"Author {self.first_name} {self.last_name}"


class Critic(Person):
    """
    Model representing a Critic, inheriting common fields from the Person model.
    This model includes properties for tracking their reviews, expertise area, and popularity.
    """

    # Critic-specific field
    expertise_area = models.CharField(
        max_length=255,
        help_text="Critic's area of expertise (e.g., literature, film).",
        null=False,
        blank=False,
    )

    # Fields for tracking critic creation and updates
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="critic_created_by",
        help_text="User who created this critic entry.",
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="critic_updated_by",
        help_text="User who last updated this critic entry.",
    )

    class Meta:
        verbose_name_plural = "Critics"

    # Properties related to the Critic's reviews and activity
    @property
    def total_activity(self):
        """
        Returns the total number of reviews given by the critic.
        """
        return self.reviews.count()

    @property
    def date_first_review(self):
        """
        Returns the date of the critic's first review.
        """
        return self.reviews.aggregate(min_date_created=Min("date_created"))[
            "min_date_created"
        ]

    @property
    def date_last_review(self):
        """
        Returns the date of the critic's last review.
        """
        return self.reviews.aggregate(max_date_created=Max("date_created"))[
            "max_date_created"
        ]

    @property
    def career_span(self):
        """
        Calculates the critic's career span in years, based on the first and last review dates.
        """
        if self.date_first_review and self.date_last_review:
            return (self.date_last_review - self.date_first_review).days // 365
        return None

    @property
    def mostly_viewed_review(self):
        """
        Returns the critic's most viewed review.
        """
        return self.reviews.order_by("-view_count").first()

    @property
    def mostly_liked_review(self):
        """
        Returns the critic's most liked review based on the number of likes.
        """
        from reviews.models import Reaction

        return (
            self.reviews.annotate(
                review_like_count=Count(
                    "reactions",
                    filter=Q(reactions__reaction_type=Reaction.ReactionType.LIKE),
                )
            )
            .order_by("-review_like_count")
            .first()
        )

    @property
    def mostly_disliked_review(self):
        """
        Returns the critic's most disliked review based on the number of dislikes.
        """
        from reviews.models import Reaction

        return (
            self.reviews.annotate(
                review_dislike_count=Count(
                    "reactions",
                    filter=Q(reactions__reaction_type=Reaction.ReactionType.DISLIKE),
                )
            )
            .order_by("-review_dislike_count")
            .first()
        )

    @property
    def popularity(self):
        """
        Calculates the critic's popularity as a score from 0 to 10 based on their view count.
        The score is scaled based on the highest view count among all critics.
        """
        max_views = (
            Critic.objects.aggregate(max_views=Max("view_count"))["max_views"] or 1
        )
        return min((self.view_count / max_views) * 10, 10)

    @property
    def ordered_reviews(self):
        """
        Returns all reviews related to this critic, annotated with like and dislike counts.
        Reviews are sorted by 'starred' status and net likes (likes minus dislikes).
        """
        from reviews.models import Reaction

        return self.reviews.annotate(
            query_likes_count=Count(
                Case(
                    When(reactions__reaction_type=Reaction.ReactionType.LIKE, then=1),
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
        ).order_by("-starred", "-query_net_likes")

    def __str__(self):
        return f"Critic {self.first_name} {self.last_name}"
