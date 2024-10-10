from datetime import date

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from people.models import Author


class BookFilterForm(forms.Form):
    # Form field for book title, not required
    title = forms.CharField(
        required=False,
        label="Title",
        help_text="Book title.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter book title",
            }
        ),
    )

    # Form field for selecting an author from a dropdown list
    author = forms.ModelChoiceField(
        queryset=Author.objects.order_by("last_name", "first_name"),
        required=False,
        label="Author",
        widget=forms.Select(attrs={"class": "form-control"}),
        help_text="Book's author.",
    )

    # Form field for publication date, with date input widget
    date_published = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
        label="Date Published",
        help_text="Book's publication date.",
    )

    # Form field for language of the book, not required
    language = forms.CharField(
        required=False,
        label="Language",
        help_text="Book's original language.",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter language",
            }
        ),
    )

    # Form field for rating selection
    rating = forms.ChoiceField(
        choices=[
            ("", "All"),
            ("1", "1 Star"),
            ("2", "2 Stars"),
            ("3", "3 Stars"),
            ("4", "4 Stars"),
            ("5", "5 Stars"),
        ],
        required=False,
        label="Rating",
        help_text="Book's rating.",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean_date_published(self):
        """Validates that the date_published is not set to a future date."""
        date_published = self.cleaned_data.get("date_published")
        if date_published:
            if date_published > date.today():
                self.add_error(
                    "date_published", _("Invalid published date - date from a future.")
                )
        return date_published

    def clean_language(self):
        """Strips any leading or trailing whitespace from the language input."""
        language = self.cleaned_data.get("language")
        if language:
            return language.strip()
        return language

    def __init__(self, *args, **kwargs):
        # Initialize the form and set up Crispy Forms helper
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = "filter-books-form"
        self.helper.form_class = "blueForms"
        self.helper.form_method = "post"
        self.helper.form_action = "login"
