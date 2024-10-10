from datetime import date, timedelta

from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _

from .models import CustomUser

PASSWORD_HELP_TEXT = """
- be at least 8 characters long
- have at least one digit, one uppercase letter, one lowercase letter and one special sign
"""


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["email", "education"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "reset-password-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "login"

    def clean_email(self):
        """Validate that the email is unique and has a valid format."""
        email = self.cleaned_data.get("email")
        email = email.strip()
        user = self.instance

        # Check if email is valid
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            raise ValidationError(_("Enter a valid email address."))

        if CustomUser.objects.filter(email=email).exclude(pk=user.pk).exists():
            raise ValidationError(_("A user with that email already exists."))

        return email

    def clean_education(self):
        """Validate education requirements."""
        education = self.cleaned_data.get("education")
        if education not in [x[0] for x in CustomUser.EDUCATION_CHOICES]:
            self.add_error("education", _(f"Invalid education selected."))
        return education


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "education",
            "date_of_birth",
            "password1",
            "password2",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "SomeUser123",
                    "required": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "example@gmail.com",
                    "required": True,
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "John",
                    "required": True,
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Doe",
                    "required": True,
                }
            ),
            "education": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "YYYY-MM-DD",
                    "type": "date",
                }
            ),
            "password1": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),
            "password2": forms.PasswordInput(
                attrs={
                    "class": "form-control",
                    "required": True,
                }
            ),
        }

        help_texts = {
            "username": _("Should be unique, readable, and easy to remember."),
            "email": _("Should be unique and valid."),
            "first_name": _("Enter your first name."),
            "last_name": _("Enter your last name."),
            "education": _("Choose your education level."),
            "date_of_birth": _("Enter your date of birth in YYYY-MM-DD format."),
            "password1": PASSWORD_HELP_TEXT,
            "password2": _("Enter the same password as above, for verification."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "create-user-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "signup"

    def clean_email(self):
        """Validate that the email is unique and has a valid format."""
        email = self.cleaned_data.get("email")
        email = email.strip()

        # Check if email is valid
        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            raise ValidationError(_("Enter a valid email address."))

        # Check if email is unique
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("A user with that email already exists."))

        return email

    def clean_username(self):
        """Validate that the username is unique."""
        username = self.cleaned_data.get("username")
        username = username.strip()
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError(_("A user with that username already exists."))
        return username

    def clean_first_name(self):
        """Formats the first name"""
        first_name = self.cleaned_data.get("first_name")
        return first_name.strip().lower().capitalize()

    def clean_last_name(self):
        """Formats the last name"""
        last_name = self.cleaned_data.get("last_name")
        return last_name.strip().lower().capitalize()

    def clean_password2(self):
        """Custom validation that checks conditions across multiple fields."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Ensure passwords match
        if password1 and password2 and password1 != password2:
            self.add_error("password2", _("The two password fields didn't match."))

        return password2

    def clean_education(self):
        """Validate education requirements."""
        education = self.cleaned_data.get("education")
        if education not in [x[0] for x in CustomUser.EDUCATION_CHOICES]:
            self.add_error("education", _(f"Invalid education selected."))
        return education

    def clean_date_of_birth(self):
        """Validates if user date of birth is valid"""
        date_of_birth = self.cleaned_data.get("date_of_birth")
        if date_of_birth:
            if date_of_birth > date.today():
                self.add_error(
                    "date_of_birth", _("Invalid date of birth - date from a future.")
                )
            if date_of_birth < date.today() - timedelta(days=100 * 365):
                self.add_error(
                    "date_of_birth", _("Invalid date of birth - user is too old.")
                )
        return date_of_birth


# Login form that uses built-in AuthenticationForm
class CustomLoginForm(AuthenticationForm):
    class Meta:
        model = AuthenticationForm
        fields = ["username", "password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "login-user-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "login"


class CustomPasswordResetForm(PasswordResetForm):
    class Meta:
        model = PasswordResetForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "reset-password-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "login"


class CustomSetPasswordForm(SetPasswordForm):
    class Meta:
        model = SetPasswordForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "reset-password-set-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "login"


class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = PasswordChangeForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "reset-password-set-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "login"
