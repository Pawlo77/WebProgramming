from datetime import date

from django.test import TestCase
from items.models import Award, Book
from people.models import Author
from users.models import CustomUser


class AwardModelTest(TestCase):
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
        self.award = Award.objects.create(
            name="Some award",
            year_awarded=2013,
            author=self.author,
            created_by=self.user,
            updated_by=self.user,
        )
        self.award.save()

    def test_age(self):
        expected_age = date.today().year - self.award.year_awarded
        self.assertEqual(self.award.age, expected_age)

    def test_str_representation(self):
        self.assertEqual(str(self.award), "Award Some award (2013) for Alice Smith")


class BookModelTest(TestCase):
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
        self.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=self.user,
            updated_by=self.user,
        )
        self.author.save()
        self.book = Book.objects.create(
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

    def test_age(self):
        expected_age = date.today().year - self.book.date_published.year
        self.assertEqual(self.book.age, expected_age)

    def test_str_representation(self):
        self.assertEqual(str(self.book), "Some Book Title 1 by Alice Smith")
