from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone
from items.models import Award, Book
from people.models import Author, Critic
from users.models import CustomUser

from .models import Reaction, Review


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="admin@example.com",
            first_name="John",
            last_name="Cena",
        )
        self.user.save()
        self.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=self.user,
            updated_by=self.user,
        )
        self.author.save()
        self.critic = Critic.objects.create(
            first_name="Bob",
            last_name="Jones",
            birth_date=date(1980, 10, 10),
            expertise_area="Literature",
            view_count=20,
            created_by=self.user,
            updated_by=self.user,
        )
        self.critic.save()
        self.book = Book(
            title="Some Book Title 1",
            author=self.author,
            date_published=date(2013, 1, 1),
            isbn="SBT1",
            language="PL",
            created_by=self.user,
            updated_by=self.user,
            pages=30,
        )
        self.book.save()
        self.review = Review.objects.create(
            content="Some review",
            critic=self.critic,
            content_type=ContentType.objects.get_for_model(Book),
            object_id=self.book.id,
        )
        self.review.save()

    def test_reactions_count(self):
        self.assertEqual(self.review.like_count, 0)
        self.assertEqual(self.review.dislike_count, 0)
        self.assertEqual(self.review.net_likes, 0)

        reaction = Reaction.objects.create(
            review=self.review,
            reaction_type=Reaction.ReactionType.LIKE,
            created_by=self.user,
            updated_by=self.user,
        )
        reaction.save()
        self.assertEqual(self.review.like_count, 1)
        self.assertEqual(self.review.dislike_count, 0)
        self.assertEqual(self.review.net_likes, 1)

        reaction.delete()
        self.assertEqual(self.review.like_count, 0)

        Reaction.objects.create(
            review=self.review,
            reaction_type=Reaction.ReactionType.DISLIKE,
            created_by=self.user,
            updated_by=self.user,
        ).save()
        self.assertEqual(self.review.like_count, 0)
        self.assertEqual(self.review.dislike_count, 1)
        self.assertEqual(self.review.net_likes, -1)

    def test_star_review(self):
        self.review.star_review(self.user)
        self.assertEqual(self.review.starred, True)
        self.assertEqual(self.review.date_starred.date(), timezone.now().date())
        self.assertEqual(self.review.starred_by, self.user)

        self.review.unstar_review(self.user)
        self.assertEqual(self.review.starred, False)
        self.assertEqual(self.review.date_starred, None)
        self.assertEqual(self.review.starred_by, None)

        user = CustomUser.objects.create_user(
            username="user2",
            password="testpass1231",
            email="user2@example.com",
            role=CustomUser.USER,
            first_name="John",
            last_name="Cena",
        )
        with self.assertRaises(PermissionDenied):
            self.review.unstar_review(user)

    def test_str_representation(self):
        self.assertEqual(
            str(self.review), "Review by Bob Jones on Some Book Title 1 by Alice Smith"
        )


class ReactionModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="admin@example.com",
            first_name="John",
            last_name="Cena",
        )
        self.user.save()
        self.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=self.user,
            updated_by=self.user,
        )
        self.author.save()
        self.critic = Critic.objects.create(
            first_name="Bob",
            last_name="Jones",
            birth_date=date(1980, 10, 10),
            expertise_area="Literature",
            view_count=20,
            created_by=self.user,
            updated_by=self.user,
        )
        self.critic.save()
        self.book = Book(
            title="Some Book Title 1",
            author=self.author,
            date_published=date(2013, 1, 1),
            isbn="SBT1",
            language="PL",
            created_by=self.user,
            updated_by=self.user,
            pages=30,
        )
        self.book.save()
        self.review = Review.objects.create(
            content="Some review",
            critic=self.critic,
            content_type=ContentType.objects.get_for_model(Book),
            object_id=self.book.id,
        )
        self.review.save()
        self.reaction = Reaction.objects.create(
            review=self.review,
            reaction_type=Reaction.ReactionType.LIKE,
            created_by=self.user,
            updated_by=self.user,
        )
        self.reaction.save()

    def test_reactions_integrity(self):
        with self.assertRaises(IntegrityError):
            Reaction.objects.create(
                review=self.review,
                reaction_type=Reaction.ReactionType.LIKE,
                created_by=self.user,
                updated_by=self.user,
            )

    def test_reactions_integrity(self):
        self.assertEqual(
            str(self.reaction),
            "admin - like on Review by Bob Jones on Some Book Title 1 by Alice Smith",
        )
