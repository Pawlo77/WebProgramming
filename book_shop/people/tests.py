from datetime import date

from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from users.models import CustomUser

from .forms import AuthorFilterForm, BaseFilterForm, CriticFilterForm
from .models import Author, Critic


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        cls.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            birth_date=date(1980, 1, 1),
            created_by=cls.user,
            updated_by=cls.user,
        )

    def test_author_creation(self):
        self.assertIsInstance(self.author, Author)
        self.assertEqual(self.author.first_name, "John")
        self.assertEqual(self.author.last_name, "Doe")

    def test_age_calculation(self):
        self.assertEqual(self.author.age, timezone.now().year - 1980)

    def test_full_name(self):
        self.assertEqual(self.author.name, "John Doe")

    def test_first_publication_date(self):
        self.assertIsNone(self.author.first_publication_date)

    def test_last_publication_date(self):
        self.assertIsNone(self.author.last_publication_date)


class CriticModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
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

    def test_critic_creation(self):
        self.assertIsInstance(self.critic, Critic)
        self.assertEqual(self.critic.first_name, "Jane")
        self.assertEqual(self.critic.last_name, "Smith")

    def test_age_calculation(self):
        self.assertEqual(self.critic.age, timezone.now().year - 1990)

    def test_full_name(self):
        self.assertEqual(self.critic.name, "Jane Smith")

    def test_total_activity(self):
        self.assertEqual(self.critic.total_activity, 0)

    def test_date_first_review(self):
        self.assertIsNone(self.critic.date_first_review)

    def test_date_last_review(self):
        self.assertIsNone(self.critic.date_last_review)


class BaseFilterFormTest(TestCase):
    """Tests for the BaseFilterForm class."""

    @classmethod
    def setUp(cls):
        cls.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            birth_date=date(1990, 1, 1),
            nationality="American",
            website="https://john-doe.com",
        )
        cls.form_data = {
            "name": "John",
            "nationality": "Americam",
            "birth_year": "1990",
            "website": "https://example.com",
        }
        cls.form = BaseFilterForm(data=cls.form_data)

    def test_clean_birth_year_valid(self):
        """Test that the birth year is cleaned correctly when valid."""
        self.form.cleaned_data = {"birth_year": "1985"}
        cleaned_year = self.form.clean_birth_year()
        self.assertEqual(cleaned_year, 1985)

    def test_clean_birth_year_future(self):
        """Test that cleaning a future year raises a validation error."""
        self.form = BaseFilterForm(data={"birth_year": str(date.today().year + 1)})
        self.assertFalse(self.form.is_valid())
        self.assertIn(
            "Invalid birth year - date from the future.", self.form.errors["birth_year"]
        )

    def test_clean_name(self):
        """Test that leading and trailing whitespace is stripped from the name."""
        self.form.cleaned_data = {"name": "   John Doe   "}
        cleaned_name = self.form.clean_name()
        self.assertEqual(cleaned_name, "John Doe")

    def test_clean_name_empty(self):
        """Test that an empty name returns None."""
        self.form.cleaned_data = {"name": ""}
        cleaned_name = self.form.clean_name()
        self.assertIsNone(cleaned_name)


class AuthorFilterFormTest(TestCase):
    """Tests for the AuthorFilterForm class."""

    @classmethod
    def setUp(cls):
        cls.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            birth_date=date(1990, 1, 1),
            nationality="American",
            website="https://john-doe.com",
        )
        cls.form_data = {
            "name": "John",
            "nationality": "American",
            "birth_year": "1990",
            "website": "https://example.com",
        }
        cls.form = AuthorFilterForm(data=cls.form_data)

    def test_initialization_with_nationality_choices(self):
        """Test that the form initializes with the correct nationality choices."""
        self.form = AuthorFilterForm()
        self.assertIn(("American", "American"), self.form.fields["nationality"].choices)

    def test_valid_form(self):
        """Test that a valid form is valid."""
        self.assertTrue(self.form.is_valid(), f"Errors: {self.form.errors}")

    def test_clean_birth_year_future(self):
        """Test that a future birth year raises a validation error."""
        self.form = AuthorFilterForm(data={"birth_year": str(date.today().year + 1)})
        self.assertFalse(self.form.is_valid())
        self.assertIn(
            "Invalid birth year - date from the future.", self.form.errors["birth_year"]
        )


class CriticFilterFormTest(TestCase):
    """Tests for the CriticFilterForm class."""

    @classmethod
    def setUp(cls):
        cls.critic = Critic.objects.create(
            first_name="Jane",
            last_name="Smith",
            birth_date=date(1985, 5, 20),
            expertise_area="Film",
            website="https://jane-smith.com",
            nationality="British",
        )
        cls.form_data = {
            "name": "Jane",
            "nationality": "British",
            "birth_year": "1985",
            "website": "https://example.com",
        }
        cls.form = CriticFilterForm(data=cls.form_data)

    def test_initialization_with_nationality_choices(self):
        """Test that the form initializes with the correct nationality choices."""
        self.assertIn(("British", "British"), self.form.fields["nationality"].choices)

    def test_valid_form(self):
        """Test that a valid form is valid."""
        self.assertTrue(self.form.is_valid(), f"Errors: {self.form.errors}")

    def test_clean_birth_year_future(self):
        """Test that a future birth year raises a validation error."""
        self.form = CriticFilterForm(data={"birth_year": str(date.today().year + 1)})
        self.assertFalse(self.form.is_valid())
        self.assertIn(
            "Invalid birth year - date from the future.", self.form.errors["birth_year"]
        )


class BaseViewTest(TestCase):
    """Base class for common setup across all view tests."""

    @classmethod
    def setUpTestData(cls):
        """Create common test data for authors and critics."""
        cls.client = Client()

        # Create test authors
        cls.author1 = Author.objects.create(
            first_name="John",
            last_name="Doe",
            birth_date=date(1990, 1, 1),
            nationality="American",
            website="https://johndoe.com",
            view_count=10,
        )
        cls.author2 = Author.objects.create(
            first_name="Jane",
            last_name="Smith",
            birth_date=date(1985, 5, 15),
            nationality="British",
            website="https://janesmith.com",
            view_count=5,
        )
        # Create test critics
        cls.critic1 = Critic.objects.create(
            first_name="Alice",
            last_name="Johnson",
            birth_date=date(1978, 3, 22),
            nationality="Canadian",
            website="https://alicejohnson.com",
            view_count=20,
        )
        cls.critic2 = Critic.objects.create(
            first_name="Bob",
            last_name="Brown",
            birth_date=date(1992, 7, 11),
            nationality="Australian",
            website="https://bobbrown.com",
            view_count=15,
        )


class AuthorDetailViewTest(BaseViewTest):
    """Tests for the AuthorDetailView."""

    def test_author_detail_view_status_code(self):
        """Test the Author Detail view returns a status code of 200."""
        response = self.client.get(reverse("author-detail", args=[self.author1.id]))
        self.assertEqual(response.status_code, 200)

    def test_author_detail_view_template_used(self):
        """Test the Author Detail view uses the correct template."""
        response = self.client.get(reverse("author-detail", args=[self.author1.id]))
        self.assertTemplateUsed(response, "author.html")

    def test_author_detail_view_context_data(self):
        """Test the context data in the Author Detail view."""
        response = self.client.get(reverse("author-detail", args=[self.author1.id]))
        self.assertEqual(response.context["author"], self.author1)


class AuthorListViewTest(BaseViewTest):
    """Tests for the AuthorListView."""

    def test_author_list_view_status_code(self):
        """Test the Author List view returns a status code of 200."""
        response = self.client.get(reverse("author-list"))
        self.assertEqual(response.status_code, 200)

    def test_author_list_view_template_used(self):
        """Test the Author List view uses the correct template."""
        response = self.client.get(reverse("author-list"))
        self.assertTemplateUsed(response, "authors.html")

    def test_author_list_view_pagination(self):
        """Test that pagination works and only 10 authors are shown at a time."""
        # Create additional authors for pagination testing
        for i in range(15):
            Author.objects.create(
                first_name=f"Author{i}",
                last_name="Test",
                birth_date=date(1990, 1, 1),
                nationality="Test",
                website="https://test.com",
                view_count=5,
            )
        response = self.client.get(reverse("author-list"))
        self.assertEqual(len(response.context["authors"]), 10)

    def test_author_filter_by_name(self):
        """Test filtering authors by name."""
        response = self.client.get(reverse("author-list"), {"name": "John"})
        self.assertIn(self.author1, response.context["authors"])
        self.assertNotIn(self.author2, response.context["authors"])

    def test_author_filter_by_nationality(self):
        """Test filtering authors by nationality."""
        response = self.client.get(reverse("author-list"), {"nationality": "British"})
        self.assertIn(self.author2, response.context["authors"])
        self.assertNotIn(self.author1, response.context["authors"])

    def test_author_filter_by_birth_year(self):
        """Test filtering authors by birth year."""
        response = self.client.get(reverse("author-list"), {"birth_year": "1990"})
        self.assertIn(self.author1, response.context["authors"])
        self.assertNotIn(self.author2, response.context["authors"])

    def test_author_filter_by_website(self):
        """Test filtering authors by website."""
        response = self.client.get(reverse("author-list"), {"website": "johndoe"})
        self.assertIn(self.author1, response.context["authors"])
        self.assertNotIn(self.author2, response.context["authors"])


class CriticDetailViewTest(BaseViewTest):
    """Tests for the CriticDetailView."""

    def test_critic_detail_view_status_code(self):
        """Test the Critic Detail view returns a status code of 200."""
        response = self.client.get(reverse("critic-detail", args=[self.critic1.id]))
        self.assertEqual(response.status_code, 200)

    def test_critic_detail_view_template_used(self):
        """Test the Critic Detail view uses the correct template."""
        response = self.client.get(reverse("critic-detail", args=[self.critic1.id]))
        self.assertTemplateUsed(response, "critic.html")

    def test_critic_detail_view_context_data(self):
        """Test the context data in the Critic Detail view."""
        response = self.client.get(reverse("critic-detail", args=[self.critic1.id]))
        self.assertEqual(response.context["critic"], self.critic1)


class CriticListViewTest(BaseViewTest):
    """Tests for the CriticListView."""

    def test_critic_list_view_status_code(self):
        """Test the Critic List view returns a status code of 200."""
        response = self.client.get(reverse("critic-list"))
        self.assertEqual(response.status_code, 200)

    def test_critic_list_view_template_used(self):
        """Test the Critic List view uses the correct template."""
        response = self.client.get(reverse("critic-list"))
        self.assertTemplateUsed(response, "critics.html")

    def test_critic_filter_by_name(self):
        """Test filtering critics by name."""
        response = self.client.get(reverse("critic-list"), {"name": "Alice"})
        self.assertIn(self.critic1, response.context["critics"])
        self.assertNotIn(self.critic2, response.context["critics"])

    def test_critic_filter_by_nationality(self):
        """Test filtering critics by nationality."""
        response = self.client.get(
            reverse("critic-list"), {"nationality": "Australian"}
        )
        self.assertIn(self.critic2, response.context["critics"])
        self.assertNotIn(self.critic1, response.context["critics"])


class URLTests(TestCase):
    """Test suite for URL patterns in the people app."""

    @classmethod
    def setUpTestData(cls):
        """Create sample data for the tests."""
        # Create test authors
        cls.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            birth_date=date(1990, 1, 1),
            nationality="American",
            website="https://johndoe.com",
            view_count=10,
        )

        # Create test critics
        cls.critic = Critic.objects.create(
            first_name="Jane",
            last_name="Smith",
            birth_date=date(1985, 5, 15),
            nationality="British",
            website="https://janesmith.com",
            view_count=5,
        )

        cls.client = Client()

    def test_author_list_url(self):
        """Test the URL for the Author List view."""
        response = self.client.get(reverse("author-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "authors.html")

    def test_author_detail_url(self):
        """Test the URL for the Author Detail view."""
        response = self.client.get(reverse("author-detail", args=[self.author.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "author.html")

    def test_critic_list_url(self):
        """Test the URL for the Critic List view."""
        response = self.client.get(reverse("critic-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "critics.html")

    def test_critic_detail_url(self):
        """Test the URL for the Critic Detail view."""
        response = self.client.get(reverse("critic-detail", args=[self.critic.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "critic.html")
