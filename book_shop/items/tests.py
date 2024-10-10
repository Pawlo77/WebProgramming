from datetime import date

from django.forms import ValidationError
from django.test import Client, TestCase
from django.urls import resolve, reverse
from people.models import Author, Critic
from reviews.models import Reaction, Review
from users.models import CustomUser

from .forms import BookFilterForm
from .models import Award, Book
from .views import AwardDetailView, BookDetailView, BookListView


class AwardModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up the test environment, creating a user, author, and award."""
        cls.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        cls.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.award = Award.objects.create(
            name="Best Author",
            description="Award for the best author of the year.",
            year_awarded=2015,
            author=cls.author,
            website="http://example.com",
            created_by=cls.user,
            updated_by=cls.user,
        )

    def test_award_creation(self):
        """Test that an award is created correctly with valid data."""
        self.assertEqual(self.award.name, "Best Author")
        self.assertEqual(self.award.year_awarded, 2015)
        self.assertEqual(self.award.author, self.author)
        self.assertEqual(
            self.award.description, "Award for the best author of the year."
        )
        self.assertEqual(self.award.website, "http://example.com")
        self.assertEqual(self.award.view_count, 0)

    def test_age(self):
        """Test the calculation of the award's age based on the year awarded."""
        current_year = date.today().year
        expected_age = current_year - self.award.year_awarded
        self.assertEqual(self.award.age, expected_age)

    def test_str_representation(self):
        """Test the string representation of the award."""
        expected_str = "Award Best Author (2015) for Alice Smith"
        self.assertEqual(str(self.award), expected_str)

    def test_unique_constraint(self):
        """Test that an IntegrityError is raised when trying to create a duplicate award."""
        with self.assertRaises(Exception):
            Award.objects.create(
                name="Best Author",
                year_awarded=2015,
                author=self.author,
                created_by=self.user,
                updated_by=self.user,
            )

    def test_view_count(self):
        """Test that the view count increments correctly."""
        self.assertEqual(self.award.view_count, 0)
        self.award.view_count += 1
        self.award.save()
        self.assertEqual(self.award.view_count, 1)

    def test_website_optional(self):
        """Test that the website field can be empty (None)."""
        award_without_website = Award.objects.create(
            name="Author of the Month",
            year_awarded=2020,
            author=self.author,
            created_by=self.user,
            updated_by=self.user,
        )
        self.assertIsNone(award_without_website.website)

    def test_photo_field(self):
        """Test that the photo field can be empty or null."""
        award_without_photo = Award.objects.create(
            name="Test Award",
            year_awarded=2020,
            author=self.author,
            created_by=self.user,
            updated_by=self.user,
        )
        self.assertFalse(bool(award_without_photo.photo))

    def test_related_author(self):
        """Test that the award is correctly linked to its author."""
        self.assertEqual(self.award.author.first_name, "Alice")
        self.assertEqual(self.award.author.last_name, "Smith")

    def test_award_creation_with_min_year(self):
        """Test that the year_awarded cannot be before a certain year."""
        with self.assertRaises(ValidationError):
            award = Award(
                name="Old Award",
                year_awarded=1900,
                # author=self.author, # no author provided
                created_by=self.user,
                updated_by=self.user,
            )
            award.full_clean()  # This should raise ValidationError


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up the test environment, creating a user, author, and book."""
        cls.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            email="user@example.com",
            role=CustomUser.ADMIN,
            first_name="John",
            last_name="Cena",
        )
        cls.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.book = Book.objects.create(
            title="Fantastic Tales",
            author=cls.author,
            date_published=date(2015, 1, 1),
            isbn="1234567890123",
            language="EN",
            pages=250,
            created_by=cls.user,
            updated_by=cls.user,
        )

    def test_book_creation(self):
        """Test that a book is created correctly with valid data."""
        self.assertEqual(self.book.title, "Fantastic Tales")
        self.assertEqual(self.book.author, self.author)
        self.assertEqual(self.book.language, "EN")
        self.assertEqual(self.book.pages, 250)

    def test_age(self):
        """Test the calculation of the book's age based on its publication date."""
        expected_age = date.today().year - self.book.date_published.year
        self.assertEqual(self.book.age, expected_age)

    def test_str_representation(self):
        """Test the string representation of the book."""
        expected_str = "Fantastic Tales by Alice Smith"
        self.assertEqual(str(self.book), expected_str)

    def test_unique_constraint(self):
        """Test that an IntegrityError is raised when trying to create a duplicate book."""
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Fantastic Tales",
                author=self.author,
                date_published=date(2015, 1, 1),
                isbn="1234567890124",
                language="EN",
                pages=200,
                created_by=self.user,
                updated_by=self.user,
            )

    def test_review_num(self):
        """Test the review_num property to ensure it correctly reflects the number of reviews."""
        review_count = self.book.review_num
        self.assertEqual(review_count, 0)

    def test_reviews(self):
        """Test the reviews property to check the handling of reactions."""
        critic = Critic.objects.create(
            first_name="Bob",
            last_name="Jones",
            birth_date=date(1980, 10, 10),
            expertise_area="Literature",
            view_count=20,
            created_by=self.user,
            updated_by=self.user,
        )
        review = Review.objects.create(
            content_object=self.book,
            content="Great book!",
            created_by=self.user,
            critic=critic,
        )

        # Creating another user to react to the review
        user2 = CustomUser.objects.create_user(
            username="anotheruser",
            password="testpass123",
            email="another@example.com",
            role=CustomUser.ADMIN,
            first_name="Some",
            last_name="User",
        )

        # Add reactions to the review
        Reaction.objects.create(
            review=review,
            reaction_type=Reaction.ReactionType.LIKE,
            created_by=self.user,
        )
        Reaction.objects.create(
            review=review,
            reaction_type=Reaction.ReactionType.DISLIKE,
            created_by=user2,
        )

        # Validate the results of the reviews
        reviews = self.book.reviews
        self.assertEqual(len(reviews), 1)  # Ensure there is one review
        self.assertEqual(reviews[0].query_likes_count, 1)  # Check likes count
        self.assertEqual(reviews[0].query_dislikes_count, 1)  # Check dislikes count
        self.assertEqual(reviews[0].query_net_likes, 0)  # Check net likes count

    def test_rating_default_value(self):
        """Test that the default rating value for a new book is 0."""
        self.assertEqual(self.book.rating, 0)

    def test_isbn_unique(self):
        """Test that ISBN is unique, and creating a book with a duplicate ISBN raises an error."""
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Another Book",
                author=self.author,
                date_published=date(2016, 1, 1),
                isbn="1234567890123",
                language="EN",
                pages=150,
                created_by=self.user,
                updated_by=self.user,
            )

    def test_pages_min_value(self):
        """Test that an error is raised when the number of pages is less than 1."""
        book = Book(
            title="Tiny Book",
            author=self.author,
            date_published=date(2016, 1, 1),
            isbn="1234567890125",
            language="EN",
            pages=0,  # Invalid value
            created_by=self.user,
            updated_by=self.user,
        )
        with self.assertRaises(ValidationError):
            book.full_clean()  # This should raise ValidationError


class BookFilterFormTest(TestCase):
    def setUp(self):
        """Set up the test environment, creating an author."""
        self.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
        )

    def test_valid_form_data(self):
        """Test that a valid form can be submitted."""
        form_data = {
            "title": "Fantastic Tales",
            "author": self.author.pk,
            "date_published": date(2015, 1, 1),
            "language": "EN",
            "rating": 4,
        }
        form = BookFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_data(self):
        """Test that a invalid form can be submitted."""
        form_data = {
            "title": "Fantastic Tales",
            "author": self.author.pk,
            "date_published": date(2030, 1, 1),  # date from feature
            "language": "EN",
            "rating": 4,
        }
        form = BookFilterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_field_labels(self):
        """Test that the form fields have correct labels."""
        form = BookFilterForm()
        self.assertEqual(form.fields["title"].label, "Title")
        self.assertEqual(form.fields["author"].label, "Author")
        self.assertEqual(form.fields["date_published"].label, "Date Published")
        self.assertEqual(form.fields["language"].label, "Language")
        self.assertEqual(form.fields["rating"].label, "Rating")


class AwardViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up test environment for Award views."""
        cls.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        cls.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.award = Award.objects.create(
            name="Best Author",
            year_awarded=2015,
            author=cls.author,
            created_by=cls.user,
            updated_by=cls.user,
        )

    def test_award_detail_view_url(self):
        """Test that the award detail view URL resolves correctly."""
        url = reverse("award-detail", kwargs={"pk": self.award.pk})
        self.assertEqual(resolve(url).func.view_class, AwardDetailView)

    def test_award_detail_view_accessible_by_name(self):
        """Test that the award detail view is accessible by its name."""
        self.client.login(username="admin", password="testpass123")
        url = reverse("award-detail", kwargs={"pk": self.award.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_award_detail_view_redirects_for_unauthenticated_user(self):
        """Test that the award detail view redirects unauthenticated users."""
        self.client.logout()  # Ensure the user is logged out
        response = self.client.get(
            reverse("award-detail", kwargs={"pk": self.award.pk})
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('award-detail', args=[self.award.pk])}",
        )


class BookViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up test environment for Book views."""
        cls.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        cls.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.book = Book.objects.create(
            title="Fantastic Tales",
            author=cls.author,
            date_published=date(2015, 1, 1),
            isbn="1234567890123",
            language="EN",
            pages=250,
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.award = Award(
            name="Old Award",
            year_awarded=1900,
            author=cls.author,
            created_by=cls.user,
            updated_by=cls.user,
        )
        cls.client = Client()

    def test_book_detail_view_url(self):
        """Test that the book detail view URL resolves correctly."""
        url = reverse("book-detail", kwargs={"pk": self.book.pk})
        self.assertEqual(resolve(url).func.view_class, BookDetailView)

    def test_book_detail_view_accessible_by_name(self):
        """Test that the book detail view is accessible by its name."""
        url = reverse("book-detail", kwargs={"pk": self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_book_list_url(self):
        """Test the URL for the Book List view."""
        response = self.client.get(reverse("book-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "books.html")

    def test_book_detail_url(self):
        """Test the URL for the Book Detail view."""
        response = self.client.get(reverse("book-detail", args=[self.book.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "book.html")

    def test_award_detail_url(self):
        """Test the URL for the Award Detail view."""
        self.award.save()  # for some reason it is not saved by default
        self.client.login(username="admin", password="testpass123")
        response = self.client.get(reverse("award-detail", args=[self.award.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "award.html")
