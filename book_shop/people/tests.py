from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from items.models import Award, Book
from reviews.models import Review
from users.models import CustomUser

from .models import Author, Critic


class AuthorModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
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

    def test_career_span(self):
        Book.objects.create(
            title="Some Book Title 1",
            author=self.author,
            date_published=date(2013, 1, 1),
            isbn="SBT1",
            language="PL",
            created_by=self.user,
            updated_by=self.user,
            pages=30,
        ).save()
        Book.objects.create(
            title="Some Book Title 2",
            author=self.author,
            date_published=date(2010, 1, 1),
            isbn="SBT2",
            language="PL",
            created_by=self.user,
            updated_by=self.user,
            pages=30,
        ).save()

        expected_span = (
            self.author.last_publication_date - self.author.first_publication_date
        ).days // 365
        self.assertEqual(self.author.career_span, expected_span)

    def test_awards(self):
        self.assertEqual(self.author.awards_num, 0)

        Award.objects.create(
            name="Some award",
            year_awarded=2013,
            author=self.author,
            created_by=self.user,
            updated_by=self.user,
        ).save()
        award = Award.objects.create(
            name="Some award 2",
            year_awarded=2015,
            author=self.author,
            created_by=self.user,
            updated_by=self.user,
        )
        award.save()

        self.assertEqual(self.author.awards_num, 2)
        self.assertEqual(self.author.first_award_date, 2013)
        self.assertEqual(self.author.last_award_date, 2015)

        award.delete()
        self.assertEqual(self.author.last_award_date, 2013)

    def test_publications_num_dates(self):
        self.assertEqual(self.author.publications_num, 0)

        Book.objects.create(
            title="Some Book Title 1",
            author=self.author,
            date_published=date(2010, 1, 1),
            isbn="SBT1",
            language="PL",
            pages=30,
            created_by=self.user,
            updated_by=self.user,
        ).save()
        self.assertEqual(self.author.publications_num, 1)
        self.assertEqual(self.author.first_publication_date, date(2010, 1, 1))
        self.assertEqual(self.author.last_publication_date, date(2010, 1, 1))

        book = Book.objects.create(
            title="Some Book Title 2",
            author=self.author,
            date_published=date(2012, 1, 1),
            isbn="SBT2",
            language="PL",
            pages=30,
            created_by=self.user,
            updated_by=self.user,
        )
        book.save()
        self.assertEqual(self.author.publications_num, 2)
        self.assertEqual(self.author.first_publication_date, date(2010, 1, 1))
        self.assertEqual(self.author.last_publication_date, date(2012, 1, 1))

        book.delete()
        self.assertEqual(self.author.publications_num, 1)
        self.assertEqual(self.author.last_publication_date, date(2010, 1, 1))

    def test_str_representation(self):
        self.assertEqual(str(self.author), "Author Alice Smith")

    def test_name(self):
        self.assertEqual(self.author.name, "Alice Smith")

    def test_age(self):
        self.assertEqual(self.author.age, 2024 - 1975)

    def test_popularity(self):
        self.assertEqual(self.author.popularity, 10)

        Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=20,
            created_by=self.user,
            updated_by=self.user,
        ).save()

        self.assertEqual(self.author.popularity, 5)

        self.author.view_count = 0
        self.assertEqual(self.author.popularity, 0)


class CriticModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            email="user@example.com",
            role=CustomUser.ADMIN,
            first_name="John",
            last_name="Cena",
        )
        self.user.save()
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

    def test_total_activity(self):
        self.assertEqual(self.critic.total_activity, 0)

        author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=self.user,
            updated_by=self.user,
        )
        author.save()
        book = Book.objects.create(
            title="Some Book Title 1",
            author=author,
            date_published=date(2013, 1, 1),
            isbn="SBT1",
            language="PL",
            created_by=self.user,
            updated_by=self.user,
            pages=30,
        )
        book.save()
        Review.objects.create(
            content="Some review",
            critic=self.critic,
            content_type=ContentType.objects.get_for_model(Book),
            object_id=book.id,
        ).save()

        self.assertEqual(self.critic.total_activity, 1)
        book = Book.objects.create(
            title="Some Book Title 2",
            author=author,
            date_published=date(2013, 1, 1),
            isbn="SBT2",
            language="PL",
            created_by=self.user,
            updated_by=self.user,
            pages=30,
        )
        book.save()
        review = Review.objects.create(
            content="Some review 2",
            critic=self.critic,
            content_type=ContentType.objects.get_for_model(Book),
            object_id=book.id,
        )
        review.save()
        self.assertEqual(self.critic.total_activity, 2)
        review.delete()
        self.assertEqual(self.critic.total_activity, 1)

    def test_str_representation(self):
        self.assertEqual(str(self.critic), "Critic Bob Jones")

    def test_date_review(self):
        self.assertIsNone(self.critic.date_first_review)
        self.assertIsNone(self.critic.date_last_review)
