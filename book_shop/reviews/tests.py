from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from items.models import Book
from people.models import Critic
from users.models import CustomUser

from .models import Reaction, Review
from .views import DislikeView, LikeView


class ReviewModelTest(TestCase):
    """Test suite for the Review model."""

    @classmethod
    def setUp(cls):
        """Set up the test environment, creating necessary instances."""
        cls.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.USER,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        cls.critic = Critic.objects.create(
            first_name="Jane",
            last_name="Smith",
            birth_date=date(1990, 1, 1),
            expertise_area="Literature",
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.review = Review.objects.create(
            content="Great book!",
            critic=cls.critic,
            created_by=cls.user,
            updated_by=cls.user,
            content_type=ContentType.objects.get_for_model(Book),
            object_id=1,
        )

    def test_review_str(self):
        """Test the string representation of the Review model."""
        self.assertEqual(
            str(self.review),
            f"Review by {self.critic.name} on {self.review.content_object}",
        )

    def test_add_like(self):
        """Test adding a like to the review."""
        self.review.add_like(self.user)
        self.assertEqual(self.review.like_count, 1)

    def test_add_dislike(self):
        """Test adding a dislike to the review."""
        self.review.add_dislike(self.user)
        self.assertEqual(self.review.dislike_count, 1)

    def test_delete_like(self):
        """Test deleting a like from the review."""
        self.review.add_like(self.user)
        self.review.delete_like(self.user)
        self.assertEqual(self.review.like_count, 0)

    def test_delete_dislike(self):
        """Test deleting a dislike from the review."""
        self.review.add_dislike(self.user)
        self.review.delete_dislike(self.user)
        self.assertEqual(self.review.dislike_count, 0)

    def test_has_liked(self):
        """Test if a user has liked the review."""
        self.assertFalse(self.review.has_liked(self.user))
        self.review.add_like(self.user)
        self.assertTrue(self.review.has_liked(self.user))

    def test_has_disliked(self):
        """Test if a user has disliked the review."""
        self.assertFalse(self.review.has_disliked(self.user))
        self.review.add_dislike(self.user)
        self.assertTrue(self.review.has_disliked(self.user))

    def test_star_review_permission_denied(self):
        """Test that a user without permission cannot star the review."""
        with self.assertRaises(PermissionDenied):
            self.review.star_review(self.user)

    def test_star_review(self):
        """Test starring a review with proper user permissions."""
        self.user.role = CustomUser.MANAGER
        self.user.save()
        self.review.star_review(self.user)
        self.assertTrue(self.review.starred)
        self.assertIsNotNone(self.review.date_starred)
        self.assertEqual(self.review.starred_by, self.user)

    def test_unstar_review_permission_denied(self):
        """Test that a user without permission cannot unstar the review."""
        with self.assertRaises(PermissionDenied):
            self.review.unstar_review(self.user)

    def test_unstar_review(self):
        """Test unstarring a review with proper user permissions."""
        self.user.role = CustomUser.MANAGER  # Set user role to Manager
        self.user.save()
        self.review.star_review(self.user)  # Star the review first
        self.review.unstar_review(self.user)
        self.assertFalse(self.review.starred)
        self.assertIsNone(self.review.date_starred)
        self.assertIsNone(self.review.starred_by)


class ReactionModelTest(TestCase):
    """Test suite for the Reaction model."""

    @classmethod
    def setUp(cls):
        """Set up the test environment, creating necessary instances."""
        cls.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        cls.critic = Critic.objects.create(
            first_name="Jane",
            last_name="Smith",
            birth_date=date(1990, 1, 1),
            expertise_area="Literature",
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.review = Review.objects.create(
            content="Great book!",
            critic=cls.critic,
            created_by=cls.user,
            updated_by=cls.user,
            content_type=ContentType.objects.get_for_model(Book),
            object_id=1,
        )
        cls.reaction = Reaction.objects.create(
            review=cls.review,
            reaction_type=Reaction.ReactionType.LIKE,
            created_by=cls.user,
            updated_by=cls.user,
        )

    def test_reaction_str(self):
        """Test the string representation of the Reaction model."""
        self.assertEqual(
            str(self.reaction),
            f"{self.user.username} - {self.reaction.reaction_type} on {self.review}",
        )

    def test_unique_together(self):
        """Test that a user cannot react multiple times to the same review."""
        with self.assertRaises(Exception):
            Reaction.objects.create(
                review=self.review,
                reaction_type=Reaction.ReactionType.DISLIKE,
                created_by=self.user,
                updated_by=self.user,
            )


class ReviewActionViewTest(TestCase):
    """Test suite for ReviewActionView and its subclasses."""

    @classmethod
    def setUp(cls):
        """Set up the test environment, creating necessary instances."""
        cls.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        cls.critic = Critic.objects.create(
            first_name="Jane",
            last_name="Smith",
            birth_date=date(1990, 1, 1),
            expertise_area="Literature",
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.review = Review.objects.create(
            content="Great book!",
            critic=cls.critic,
            created_by=cls.user,
            updated_by=cls.user,
            content_type=ContentType.objects.get_for_model(Book),
            object_id=1,
        )

    def test_like_view_requires_login(self):
        """Test that LikeView requires user to be logged in."""
        response = self.client.post(reverse("like_review", args=[self.review.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_like_review(self):
        """Test liking a review."""
        self.client.login(username="admin", password="testpass123")
        response = self.client.post(reverse("like_review", args=[self.review.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "liked": True,
                "like_count": 1,
                "dislike_count": 0,
            },
        )

    def test_unlike_review(self):
        """Test unliking a review."""
        self.client.login(username="admin", password="testpass123")
        self.client.post(reverse("like_review", args=[self.review.pk]))  # Like first
        response = self.client.post(
            reverse("like_review", args=[self.review.pk])
        )  # Toggle like
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "liked": False,
                "like_count": 0,
                "dislike_count": 0,
            },
        )

    def test_dislike_view_requires_login(self):
        """Test that DislikeView requires user to be logged in."""
        response = self.client.post(reverse("dislike_review", args=[self.review.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dislike_review(self):
        """Test disliking a review."""
        self.client.login(username="admin", password="testpass123")
        response = self.client.post(reverse("dislike_review", args=[self.review.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "disliked": True,
                "like_count": 0,
                "dislike_count": 1,
            },
        )

    def test_undislike_review(self):
        """Test undisliking a review."""
        self.client.login(username="admin", password="testpass123")
        self.client.post(
            reverse("dislike_review", args=[self.review.pk])
        )  # Dislike first
        response = self.client.post(
            reverse("dislike_review", args=[self.review.pk])
        )  # Toggle dislike
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "disliked": False,
                "like_count": 0,
                "dislike_count": 0,
            },
        )
