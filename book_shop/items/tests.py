from datetime import date

from django.forms import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import resolve, reverse
from items.models import Award, Book
from people.models import Author, Critic
from reviews.models import Reaction, Review
from users.models import CustomUser

from .forms import BookFilterForm
from .models import Award, Book
from .views import AwardDetailView, BookDetailView, BookListView


class AwardModelTest(TestCase):
    def setUp(self):
        """Set up the test environment, creating a user, author, and award."""
        self.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        self.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=self.user,
            updated_by=self.user,
        )
        self.award = Award.objects.create(
            name="Best Author",
            description="Award for the best author of the year.",
            year_awarded=2015,
            author=self.author,
            website="http://example.com",
            created_by=self.user,
            updated_by=self.user,
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
        expected_age = date.today().year - self.award.year_awarded
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
        # Explicitly create the award without a photo
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


class BookModelTest(TestCase):
    def setUp(self):
        """Set up the test environment, creating a user, author, and book."""
        self.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            email="user@example.com",
            role=CustomUser.ADMIN,
            first_name="John",
            last_name="Cena",
        )
        self.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=self.user,
            updated_by=self.user,
        )
        self.book = Book.objects.create(
            title="Fantastic Tales",
            author=self.author,
            date_published=date(2015, 1, 1),
            isbn="1234567890123",
            language="EN",
            pages=250,
            created_by=self.user,
            updated_by=self.user,
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

        # Assert that a validation error is raised when trying to clean the book instance
        with self.assertRaises(Exception) as context:
            book.full_clean()

        # Verify that the pages error is included in the raised exception
        self.assertIn(
            "pages", context.exception.message_dict
        )  # Check if 'pages' key is in the error dict
        self.assertIn(
            "Ensure this value is greater than or equal to 1.",
            context.exception.message_dict["pages"],
        )


class BookFilterFormTest(TestCase):
    def setUp(self):
        """Set up test data for form tests."""
        self.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=None,
            updated_by=None,
        )

    def test_form_valid_with_no_data(self):
        """Test that the form is valid when no data is submitted."""
        form = BookFilterForm(data={})
        self.assertTrue(form.is_valid())  # Validate the form
        self.assertEqual(
            form.cleaned_data,
            {
                "title": "",
                "author": None,
                "date_published": None,
                "language": "",
                "rating": "",
            },
        )

    def test_form_valid_with_valid_data(self):
        """Test that the form is valid when given valid data."""
        form_data = {
            "title": "Fantastic Tales",
            "author": self.author.id,
            "date_published": date(2015, 1, 1),
            "language": "EN",
            "rating": "5",
        }
        form = BookFilterForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "Fantastic Tales")
        self.assertEqual(form.cleaned_data["author"], self.author)
        self.assertEqual(form.cleaned_data["date_published"], date(2015, 1, 1))
        self.assertEqual(form.cleaned_data["language"], "EN")
        self.assertEqual(form.cleaned_data["rating"], "5")

    def test_clean_date_published_future_date(self):
        """Test that the form raises a validation error for future dates."""
        future_date = date.today().replace(year=date.today().year + 1)
        form_data = {"date_published": future_date}
        form = BookFilterForm(data=form_data)
        self.assertFalse(form.is_valid())  # Check if the form is not valid
        self.assertIn(
            "date_published", form.errors
        )  # Check that there are errors for date_published
        self.assertIn(
            "Invalid published date - date from a future.",
            form.errors["date_published"],
        )

    def test_clean_language_strips_whitespace(self):
        """Test that the clean_language method strips whitespace."""
        form_data = {"language": "  English  "}
        form = BookFilterForm(data=form_data)
        form.is_valid()  # Run validation
        self.assertEqual(form.cleaned_data["language"], "English")

    def test_form_author_label(self):
        """Test that the author label is correct."""
        form = BookFilterForm()
        expected_label = f"{self.author.first_name} {self.author.last_name}"
        self.assertEqual(
            form.fields["author"].label_from_instance(self.author), expected_label
        )

    def test_invalid_rating(self):
        """Test that the form is invalid when an invalid rating is provided."""
        form_data = {"rating": "6"}  # Invalid rating not in choices
        form = BookFilterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Select a valid choice.", form.errors["rating"][0]
        )  # Adjusted to check the first error

    def test_rating_default_value(self):
        """Test that the form defaults rating to 'All'."""
        form = BookFilterForm(data={})  # Initialize the form with no data
        self.assertTrue(form.is_valid())  # Ensure the form is valid
        self.assertEqual(
            form.cleaned_data["rating"], ""
        )  # Check the cleaned data for rating


class AwardDetailViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        self.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=self.user,
            updated_by=self.user,
        )
        self.award = Award.objects.create(
            name="Best Author",
            description="Award for the best author of the year.",
            year_awarded=2015,
            author=self.author,
            website="http://example.com",
            created_by=self.user,
            updated_by=self.user,
        )

    def test_award_detail_view(self):
        """Test that the award detail view displays the award correctly."""
        response = self.client.get(
            reverse("award-detail", kwargs={"pk": self.award.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "award.html")
        self.assertEqual(response.context["award"], self.award)

    def test_award_view_increments_views(self):
        """Test that the views count increments when award detail is accessed."""
        initial_views = self.award.view_count  # Assuming views is a field in Award
        self.client.get(reverse("award-detail", kwargs={"pk": self.award.pk}))
        self.award.refresh_from_db()  # Reload the award instance
        self.assertEqual(self.award.view_count, initial_views + 1)


class BookDetailViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="admin",
            password="testpass123",
            role=CustomUser.ADMIN,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        self.author = Author.objects.create(
            first_name="Alice",
            last_name="Smith",
            birth_date=date(1975, 5, 5),
            view_count=10,
            created_by=self.user,
            updated_by=self.user,
        )

        self.book = Book.objects.create(
            title="Fantastic Tales",
            author=self.author,
            date_published=date(2015, 1, 1),
            isbn="1234567890124",
            language="EN",
            pages=200,
            created_by=self.user,
            updated_by=self.user,
        )

    def test_book_detail_view(self):
        """Test that the book detail view displays the book correctly."""
        response = self.client.get(reverse("book-detail", kwargs={"pk": self.book.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "book.html")
        self.assertEqual(response.context["book"], self.book)

    def test_book_detail_view_like_statuses(self):
        """Test that the like statuses are included in the context."""
        response = self.client.get(reverse("book-detail", kwargs={"pk": self.book.pk}))
        self.assertIn("like_statuses_active", response.context)
        self.assertIn("like_statuses_unactive", response.context)
        self.assertIn("disliked_statuses_active", response.context)
        self.assertIn("disliked_statuses_unactive", response.context)


class UrlsTest(SimpleTestCase):
    def test_book_list_url(self):
        url = reverse("book-list")
        self.assertEqual(url, "/items/books")  # Ensure the trailing slash is included
        self.assertEqual(resolve(url).func.view_class, BookListView)

    def test_book_detail_url(self):
        url = reverse("book-detail", kwargs={"pk": 1})
        self.assertEqual(
            url, "/items/books/1/"
        )  # Ensure the trailing slash is included
        self.assertEqual(resolve(url).func.view_class, BookDetailView)

    def test_award_detail_url(self):
        url = reverse("award-detail", kwargs={"pk": 1})
        self.assertEqual(
            url, "/items/awards/1/"
        )  # Ensure the trailing slash is included
        self.assertEqual(resolve(url).func.view_class, AwardDetailView)
