# views do not need to be tested as they are just ui-changed django views

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, UserUpdateForm
from .models import CustomUser, CustomUserManager
from .validators import CustomPasswordValidator


class CustomUserManagerTest(TestCase):
    """Test suite for CustomUserManager."""

    def setUp(self):
        """Set up the test environment by creating necessary groups for testing."""
        if not Group.objects.filter(name="Admin").exists():
            Group.objects.create(name="Admin")
        if not Group.objects.filter(name="Staff").exists():
            Group.objects.create(name="Staff")

    def test_create_user(self):
        """Test creating a regular user with valid credentials."""
        user = CustomUser.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        # Check user attributes
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "user@example.com")
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.role, CustomUser.USER)

        # Verify password is hashed
        self.assertNotEqual(user.password, "testpass123")
        self.assertTrue(user.check_password("testpass123"))

    def test_create_user_missing_username(self):
        """Test that ValueError is raised when username is missing."""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                username=None,
                email="user@example.com",
                password="testpass123",
                first_name="Johnny",
                last_name="Doe",
            )
        self.assertEqual(str(context.exception), _("The username must be set"))

    def test_create_user_missing_email(self):
        """Test that ValueError is raised when email is missing."""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                username="testuser",
                email=None,
                password="testpass123",
                first_name="John",
                last_name="Doe",
            )
            self.assertEqual(str(context.exception), _("The Email must be set"))

    def test_create_user_missing_first_name(self):
        """Test that ValueError is raised when first name is missing."""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                username="testuser",
                email="user@example.com",
                password="testpass123",
                first_name=None,
                last_name="Doe",
            )
            self.assertEqual(str(context.exception), _("The first name must be set"))

    def test_create_user_missing_last_name(self):
        """Test that ValueError is raised when last name is missing."""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                username="testuser",
                email="user@example.com",
                password="testpass123",
                first_name="John",
                last_name=None,
            )
            self.assertEqual(str(context.exception), _("The last name must be set"))

    def test_create_admin(self):
        """Test creating an admin user and ensure all properties are set correctly."""
        admin_user = CustomUser.objects.create_admin(
            first_name="John",
            last_name="Doe",
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
        )
        # Check user attributes
        self.assertEqual(admin_user.username, "adminuser")
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)
        self.assertEqual(admin_user.role, CustomUser.ADMIN)

        # Verify group assignment
        self.assertTrue(admin_user.groups.filter(name="Admin").exists())
        self.assertTrue(admin_user.groups.filter(name="Staff").exists())

    def test_create_manager(self):
        """Test creating a manager user and ensure all properties are set correctly."""
        manager_user = CustomUser.objects.create_manager(
            first_name="John",
            last_name="Doe",
            username="manageruser",
            email="manager@example.com",
            password="managerpass123",
        )
        # Check user attributes
        self.assertEqual(manager_user.username, "manageruser")
        self.assertEqual(manager_user.email, "manager@example.com")
        self.assertFalse(manager_user.is_superuser)
        self.assertTrue(manager_user.is_staff)
        self.assertEqual(manager_user.role, CustomUser.MANAGER)

        # Verify group assignment
        self.assertTrue(manager_user.groups.filter(name="Staff").exists())
        self.assertFalse(manager_user.groups.filter(name="Admin").exists())

    def test_create_superuser(self):
        """Test creating a superuser and ensure all properties are set correctly."""
        superuser = CustomUser.objects.create_superuser(
            first_name="John",
            last_name="Doe",
            username="superuser",
            email="super@example.com",
            password="superpass123",
        )
        # Check user attributes
        self.assertEqual(superuser.username, "superuser")
        self.assertEqual(superuser.email, "super@example.com")
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_group_assignment_failure(self):
        """Test that ValueError is raised when trying to assign a non-existing group."""
        with self.assertRaises(ValueError) as context:
            user = CustomUser.objects.create_manager(
                first_name="Max",
                last_name="Stark",
                username="testmanager",
                email="manager@example.com",
                password="managerpass123",
                role=CustomUser.MANAGER,
            )
            user.save()
            CustomUserManager()._assign_groups(user, ["NonExistentGroup"])
        self.assertEqual(
            str(context.exception), _("Group 'NonExistentGroup' does not exist.")
        )


class CustomUserModelTest(TestCase):
    """Test suite for the CustomUser model."""

    def test_str_method(self):
        """Test the string representation of the CustomUser model."""
        user = CustomUser.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.assertEqual(str(user), "testuser")

    def test_user_role(self):
        """Test user roles for different user types."""
        user = CustomUser.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.assertEqual(user.role, CustomUser.USER)

        manager = CustomUser.objects.create_manager(
            first_name="John",
            last_name="Kowalski",
            username="manageruser",
            email="manager@example.com",
            password="managerpass123",
        )
        self.assertEqual(manager.role, CustomUser.MANAGER)

        admin = CustomUser.objects.create_admin(
            first_name="John",
            last_name="Stark",
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
        )
        self.assertEqual(admin.role, CustomUser.ADMIN)

    def test_save_method(self):
        """Test the save method to ensure role affects is_superuser and is_staff."""
        user = CustomUser(
            username="testuser", email="user@example.com", password="testpass123"
        )

        # Test ADMIN role
        user.role = CustomUser.ADMIN
        user.save()
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

        # Test MANAGER role
        user.role = CustomUser.MANAGER
        user.save()
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_staff)

        # Test USER role
        user.role = CustomUser.USER
        user.save()
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_user_email_unique_constraint(self):
        """Test that email must be unique."""
        CustomUser.objects.create_user(
            first_name="Mark",
            last_name="Stark",
            username="testuser1",
            email="unique@example.com",
            password="testpass123",
        )
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                first_name="Mark",
                last_name="Doe",
                username="testuser2",
                email="unique@example.com",  # Duplicate email
                password="testpass456",
            )

    def test_date_fields(self):
        """Test that date fields are set correctly on user creation."""
        user = CustomUser.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.assertIsNotNone(user.date_joined)  # Should be set automatically
        self.assertIsNotNone(user.date_updated)  # Should be set automatically

    def test_first_and_last_name_required(self):
        """Test that first and last names are required fields."""
        with self.assertRaises(ValueError) as context:
            CustomUser.objects.create_user(
                username="testuser",
                email="user@example.com",
                password="testpass123",
                first_name=None,
                last_name="Doe",
            )
        self.assertEqual(str(context.exception), _("The first name must be set"))


class UserUpdateFormTest(TestCase):
    """Test suite for UserUpdateForm."""

    def setUp(self):
        """Set up a user for testing."""
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="user@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            education=CustomUser.HIGH,
            date_of_birth=date(2000, 1, 1),
        )

    def test_valid_form(self):
        """Test the UserUpdateForm with valid data."""
        form_data = {
            "email": "new_email@example.com",
            "education": CustomUser.PRIMARY,
        }
        form = UserUpdateForm(instance=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.email, "new_email@example.com")
        self.assertEqual(updated_user.education, CustomUser.PRIMARY)

    def test_invalid_email_format(self):
        """Test the UserUpdateForm with invalid email format."""
        form_data = {
            "email": "invalid-email",
            "education": "Bachelors",
        }
        form = UserUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("education", form.errors)

    def test_email_not_unique(self):
        """Test the UserUpdateForm with a non-unique email."""
        CustomUser.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="testpass123",
            first_name="Jane",
            last_name="Doe",
            education="Bachelors",
            date_of_birth=date(2000, 1, 1),
        )
        form_data = {
            "email": "another@example.com",  # This email already exists
            "education": "Bachelors",
        }
        form = UserUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("education", form.errors)

    def test_invalid_education(self):
        """Test the UserUpdateForm with invalid education."""
        form_data = {
            "email": "valid_email@example.com",
            "education": "InvalidEducation",  # Not a valid choice
        }
        form = UserUpdateForm(instance=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("education", form.errors)


class CustomUserCreationFormTest(TestCase):
    """Test suite for CustomUserCreationForm."""

    def test_valid_form(self):
        """Test the CustomUserCreationForm with valid data."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "education": CustomUser.PRIMARY,
            "date_of_birth": date(1990, 1, 1),
            "password1": "Testpass123!",
            "password2": "Testpass123!",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")

    def test_invalid_email_format(self):
        """Test the CustomUserCreationForm with invalid email format."""
        form_data = {
            "username": "newuser",
            "email": "invalid-email",
            "first_name": "New",
            "last_name": "User",
            "education": "Bachelors",
            "date_of_birth": date(1990, 1, 1),
            "password1": "Testpass123!",
            "password2": "Testpass123!",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_non_unique_username(self):
        """Test the CustomUserCreationForm with a non-unique username."""
        CustomUser.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="password",
            first_name="Existing",
            last_name="User",
            education="Bachelors",
            date_of_birth=date(1990, 1, 1),
        )
        form_data = {
            "username": "existinguser",  # This username already exists
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "education": "Bachelors",
            "date_of_birth": date(1990, 1, 1),
            "password1": "Testpass123!",
            "password2": "Testpass123!",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("education", form.errors)

    def test_passwords_do_not_match(self):
        """Test the CustomUserCreationForm with mismatched passwords."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "education": "Bachelors",
            "date_of_birth": date(1990, 1, 1),
            "password1": "Testpass123!",
            "password2": "DifferentPass123!",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)
        self.assertIn("education", form.errors)

    def test_invalid_education(self):
        """Test the CustomUserCreationForm with invalid education."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "education": "InvalidEducation",  # Not a valid choice
            "date_of_birth": date(1990, 1, 1),
            "password1": "Testpass123!",
            "password2": "Testpass123!",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("education", form.errors)

    def test_date_of_birth_in_future(self):
        """Test the CustomUserCreationForm with future date of birth."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "education": "Bachelors",
            "date_of_birth": date.today() + timedelta(days=1),  # Future date
            "password1": "Testpass123!",
            "password2": "Testpass123!",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertIn("education", form.errors)

    def test_date_of_birth_too_old(self):
        """Test the CustomUserCreationForm with a date of birth that is too old."""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "education": "Bachelors",
            "date_of_birth": date.today() - timedelta(days=100 * 365 + 1),  # Too old
            "password1": "Testpass123!",
            "password2": "Testpass123!",
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)
        self.assertIn("education", form.errors)


class CustomPasswordValidatorTest(TestCase):
    def setUp(self):
        self.validator = CustomPasswordValidator()

    def test_password_with_spaces(self):
        """Test that a password containing spaces raises a ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate("Invalid Password@123")
        self.assertEqual(
            context.exception.messages[0], _("Password cannot contain spaces.")
        )

    def test_password_without_lowercase(self):
        """Test that a password without lowercase letters raises a ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate("INVALIDPASSWORD123@")
        self.assertEqual(
            context.exception.messages[0],
            _("Password must contain at least one lowercase letter."),
        )

    def test_password_without_uppercase(self):
        """Test that a password without uppercase letters raises a ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate("invalidpassword123@")
        self.assertEqual(
            context.exception.messages[0],
            _("Password must contain at least one uppercase letter."),
        )

    def test_password_without_digit(self):
        """Test that a password without digits raises a ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate("InvalidPassword@")
        self.assertEqual(
            context.exception.messages[0],
            _("Password must contain at least one digit."),
        )

    def test_password_without_special_character(self):
        """Test that a password without special characters raises a ValidationError."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate("InvalidPassword1")
        self.assertEqual(
            context.exception.messages[0],
            _("Password must contain at least one special character."),
        )

    def test_valid_password(self):
        """Test that a valid password does not raise a ValidationError."""
        try:
            self.validator.validate("ValidPassword1@")
        except ValidationError:
            self.fail("validate() raised ValidationError unexpectedly!")
