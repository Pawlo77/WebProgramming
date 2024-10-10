from datetime import date

from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Author, Critic


class BaseFilterForm(forms.Form):
    """Base form for common filtering fields (name, nationality, birth year, website)."""

    name = forms.CharField(
        required=False,
        label="Name",
        help_text="Person's name.",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter name"}
        ),
    )
    nationality = forms.ChoiceField(
        required=False,
        label="Nationality",
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Person's nationality.",
    )
    birth_year = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "YYYY",
                "pattern": "[0-9]{4}",
                "title": "Enter a valid year",
                "class": "form-control",
            }
        ),
        label="Birth Year",
        max_length=4,
        help_text="Person's birth year.",
    )
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "https://example.com",
                "class": "form-control",
            }
        ),
        label="Website",
        help_text="Person's official website or portfolio link.",
    )

    def __init__(self, *args, **kwargs):
        """Initialize the form and setup Crispy Forms."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "blueForms"
        self.helper.form_action = "login"  # Replace with correct form action URL

    def clean_birth_year(self):
        """Ensure that birth year is not set to a future year."""
        birth_year = self.cleaned_data.get("birth_year")
        if birth_year:
            birth_year = int(birth_year)
            if birth_year > date.today().year:
                self.add_error(
                    "birth_year", _("Invalid birth year - date from the future.")
                )
        return birth_year

    def clean_name(self):
        """Strip leading and trailing whitespace from the name field."""
        name = self.cleaned_data.get("name")
        return name.strip() if name else None


class AuthorFilterForm(BaseFilterForm):
    """Form for filtering authors."""

    def __init__(self, *args, **kwargs):
        """Initialize the author form and set nationality choices."""
        super().__init__(*args, **kwargs)
        # Set nationality choices dynamically based on distinct values from Author model
        self.fields["nationality"].choices = [
            (nationality, nationality)
            for nationality in Author.objects.values_list("nationality", flat=True)
            .distinct()
            .order_by("nationality")
        ]


class CriticFilterForm(BaseFilterForm):
    """Form for filtering critics."""

    def __init__(self, *args, **kwargs):
        """Initialize the critic form and set nationality choices."""
        super().__init__(*args, **kwargs)
        # Set nationality choices dynamically based on distinct values from Critic model
        self.fields["nationality"].choices = [
            (nationality, nationality)
            for nationality in Critic.objects.values_list("nationality", flat=True)
            .distinct()
            .order_by("nationality")
        ]
